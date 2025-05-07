import gymnasium as gym
import numpy as np
import subprocess
import socket
import time
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy

from ciberEnv1.ciberEnv1 import CiberEnv1

SIM_IP = "127.0.0.1"
SIM_PORT = 6000

class CiberCorridorEnv(CiberEnv1):
    def __init__(self) -> None:
        super().__init__(gym.spaces.Box(low=-1.0, high=100.0,shape=(5,),dtype=np.float32),
                         gym.spaces.Box(low=-0.15, high=0.15,shape=(2,),dtype=np.float32),
                         ["--param","../Labs/pc-2425/C1-env-config.xml",
                          "--lab","../Labs/pc-2425/C1-lab.xml", "--grid", "../Labs/pc-2425/C1-grid.xml",
                          "--scoring","1"]
        )

        self.prev_score = 0 

    def step(self, action):
        self.agentapi.driveMotors(action[0], action[1])
        self.agentapi.readSensors()

        obs_ir = self.agentapi.measures.irSensor
        obs = np.append(np.array(obs_ir), np.array(self.agentapi.measures.collision))

        terminated = self.agentapi.measures.time == self.agentapi.simTime
        truncated = self.agentapi.measures.score < 0

        current_score = self.agentapi.measures.score
        score_ready = self.agentapi.measures.scoreReady
        score_diff = current_score - self.prev_score
        self.prev_score = current_score

        reward = 0.0

        if score_diff > 0:
            reward += score_diff  
        else:
            reward -= 1.0  

        if self.agentapi.measures.collision:
            reward -= 5.0

        if terminated or truncated:
            print("SCORE ENV", self.agentapi.measures.score)

        return obs, reward, terminated, truncated, {"score": self.agentapi.measures.score}

    def reset(self, seed=None):
        super().reset()
        self.prev_score = 0  
        obs_ir = self.agentapi.measures.irSensor
        obs = np.append(np.array(obs_ir), np.array(self.agentapi.measures.collision))
        return obs, {"score": 0}

    def close(self):
        self.sim_proc.terminate()

c_env = CiberCorridorEnv()

model = PPO("MlpPolicy", c_env, verbose=1)
model.learn(500000)

model.save("cibercorridorenv_ppo_1")

mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
print("evaluate mean", mean_reward, "std", std_reward)

c_env.close()
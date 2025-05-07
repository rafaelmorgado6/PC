import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO

from ciberEnv1.ciberEnv1 import CiberEnv1

SIM_IP = "127.0.0.1"
SIM_PORT = 6000

class CiberCorridorEnv(CiberEnv1):
    def __init__(self) -> None:
        super().__init__(gym.spaces.Box(low=-1.0, high=100.0, shape=(5,), dtype=np.float32),
                         gym.spaces.Box(low=-0.15, high=0.15, shape=(2,), dtype=np.float32),
                         ["--param", "../Labs/pc-2425/C1-env-config.xml",
                          "--lab", "../Labs/pc-2425/C1-lab.xml", "--grid", "../Labs/pc-2425/C1-grid.xml",
                          "--scoring", "1"]
                         )

    def step(self, action):
        self.agentapi.driveMotors(action[0], action[1])
        self.agentapi.readSensors()

        obs_ir = self.agentapi.measures.irSensor
        obs = np.append(np.array(obs_ir), np.array(self.agentapi.measures.collision))

        terminated = self.agentapi.measures.time == self.agentapi.simTime
        truncated = self.agentapi.measures.score < 0

        reward = self.agentapi.measures.score - self.prev_score
        if self.agentapi.measures.collision:
            reward -= 5.0

        self.prev_score = self.agentapi.measures.score

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

model_file = "cibercorridorenv_ppo_1"  
model = PPO.load(model_file)
print(f"Model {model_file} loaded successfully.")

scores = []
for i in range(10):
    obs, info = c_env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = c_env.step(action)
        done = terminated or truncated
    scores.append(info["score"])

mean_score = np.mean(scores)
std_score = np.std(scores)
print(f"Mean Score: {mean_score}, Standard Deviation: {std_score}")

c_env.close()

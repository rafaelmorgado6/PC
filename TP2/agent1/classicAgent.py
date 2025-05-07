import sys
import time
from croblink import *
from math import *

# Controladores
class PIDController:
    def __init__(self, Kp, Ki, Kd, dt):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.prev_error = 0
        self.error_sum = 0

    def control(self, error):
        self.error_sum += error * self.dt
        error_dot = (error - self.prev_error) / self.dt
        self.prev_error = error
        return self.Kp * error + self.Ki * self.error_sum + self.Kd * error_dot

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        super().__init__(rob_name, rob_id, angles, host)
        self.pid_controller = PIDController(Kp=1, Ki=0.05, Kd=0.5, dt=0.1) # Kp=0.8, Ki=0.05, Kd=0.3, dt=0.1
        self.base_speed = 0.1

    def wander(self):
        # Configuração dos sensores IR com mapeamento [front, left, right, back]
        front = self.measures.irSensor[0]
        left = self.measures.irSensor[1]
        right = self.measures.irSensor[2]
        back = self.measures.irSensor[3]

        # Controle para evitar colisões frontais
        print("front sensor: " + str(front))
        print("left sensor: " + str(left))
        print("right sensor: " + str(right))

        if front > 1 or left > 2.5 or right > 2.5:
            if left > right:
                print("Evading: Turning Right")
                self.driveMotors(0.1, -0.1)  # Girar à direita
                #time.sleep(0.2)
                return
            else:
                print("Evading: Turning Left")
                self.driveMotors(-0.1, 0.1)  # Girar à esquerda
                #time.sleep(0.2)
                return

        # Controle lateral com base nos sensores laterais
        error = left - right

        # Adicionar zona morta para pequenos erros
        if abs(error) < 0.5:  # Zona morta para evitar ajustes desnecessários
            correction = 0
        else:
            correction = self.pid_controller.control(error)

        # Ajuste da velocidade das rodas
        left_speed = self.base_speed - correction
        right_speed = self.base_speed + correction

        # Limitar as velocidades para evitar ajustes bruscos
        left_speed = max(min(left_speed, 0.15), 0.05)
        right_speed = max(min(right_speed, 0.15), 0.05)

        #print(f"Navigating: Left Speed: {left_speed}, Right Speed: {right_speed}, Correction: {correction}, Error: {error}")
        self.driveMotors(left_speed, right_speed)

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()

        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.robName + " exiting")
                quit()

            # Navegar pelo labirinto
            self.wander()

            time.sleep(0.1)  # Tempo entre as atualizações


    def close(self):
        """Método para liberar recursos."""
        print("Closing connection.")
        self.sock.close()

if __name__ == '__main__':
    rob_name = "ClassicPIDAgent"
    host = "localhost"
    rob = MyRob(rob_name, 1, [0.0, 60.0, -60.0, 180.0], host)  # Ângulos ajustados para [front, left, right, back]

    try:
        rob.run()
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    finally:
        rob.close()

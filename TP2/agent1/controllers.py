import argparse
import numpy as np
import matplotlib.pyplot as plt


class DampedMassSpringSystem:
    def __init__(self, m, c, k, dt):
        self.m = m
        self.c = c
        self.k = k
        self.dt = dt

    def step(self, x, u):
        x1, x2 = x
        x1_dot = x2
        x2_dot = (-self.k * x1 - self.c * x2 + u) / self.m
        return np.array([x1_dot, x2_dot]) * self.dt + x

# Baseia-se em condições pré-definidas para tomar decisões
class BangBangController:
    def control(self, error):
        if error > 0:
            return 10
        else:
            return -10

# Ajusta a entrada do sistema proporcionalmente ao erro: u(t)=Kp*e(t)
class ProportionalController:
    def __init__(self, Kp):
        self.Kp = Kp

    def control(self, error):
        return self.Kp * error

# Considera o erro acumulado ao longo do tempo para corrigir desvios persistentes
class PIController:
    def __init__(self, Kp, Ki, dt):
        self.Kp = Kp
        self.Ki = Ki
        self.error_sum = 0
        self.dt = dt

    def control(self, error):
        self.error_sum += error*dt
        return self.Kp * error + self.Ki * self.error_sum

# Reage à taxa de variação do erro para evitar mudanças abruptas    
class PDController:
    def __init__(self, Kp, Kd, dt):
        self.Kp = Kp
        self.Kd = Kd
        self.dt = dt
        self.prev_error = 0

    def control(self, error):
        error_dot = (error - self.prev_error)/dt
        self.prev_error = error
        u = self.Kp * error + self.Kd * error_dot
        return u

class PIDController:
    def __init__(self, Kp, Ki, Kd, dt):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.error_sum = 0
        self.prev_error = 0

    def control(self, error):
        self.error_sum += error * dt
        error_dot = (error - self.prev_error)/dt
        self.prev_error = error
        u = self.Kp * error + self.Ki * self.error_sum + self.Kd * error_dot
        return u

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Control System Simulation')
parser.add_argument('--controller', type=str, default='P', choices=['BB', 'P', 'PI','PD','PID'], help='Choose a controller (default: P)')
parser.add_argument('--Kp', type=float, default=1.0, help='Proportional gain')
parser.add_argument('--Ki', type=float, default=1.0, help='Integral gain')
parser.add_argument('--Kd', type=float, default=1.0, help='Derivative gain')
parser.add_argument('--m', type=float, default=1.0, help='System parameter m')
parser.add_argument('--c', type=float, default=1.0, help='System parameter c')
parser.add_argument('--k', type=float, default=1.0, help='System parameter k')
args = parser.parse_args()

# Simulation parameters
dt = 0.1
T = 20
setpoint = 10
initial_state = np.array([0, 0])

# System and controller
# system = SecondOrderSystem(args.a1, args.a2, args.b1, args.b2)
system = DampedMassSpringSystem(args.m, args.c, args.k, dt)

if args.controller == 'BB':
    controller = BangBangController()
elif args.controller == 'P':
    controller = ProportionalController(args.Kp)
elif args.controller == 'PI':
    controller = PIController(args.Kp, args.Ki, dt)
elif args.controller == 'PD':
    controller = PDController(args.Kp, args.Kd, dt)
else:
    controller = PIDController(args.Kp, args.Ki, args.Kd, dt)

# Simulation loop
time = np.arange(0, T, dt)
x = np.zeros((len(time), 2))
x[0] = initial_state

for t in range(1, len(time)):
    error = setpoint - x[t-1, 0]
    u = controller.control(error)
    x[t] = system.step(x[t-1], u)

# Plot the results
plt.plot(time, x[:, 0], label='System Response')
plt.plot(time, setpoint * np.ones_like(time), label='Setpoint')
plt.xlabel('Time')
plt.ylabel('State')
plt.legend()
plt.grid(True)
plt.show()

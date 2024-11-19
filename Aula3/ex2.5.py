'''script Python para controlar um robô, utilizando um filtro de Kalman 
para estimar a distância até uma parede com base em medições de um sensor 
infravermelho (IR).'''
import sys
from croblink import *
from math import *
import time

#  CHECK WHAT VALUE THIS SHOULD BE
measureVariance = 1

def kalmanFilter(measure, oldMeasure, oldVar, measureVariance):

    # Ganho de Kalman determina quanto da nova medição deve ser incorporada à estimativa anterior.
    # Um ganho maior significa que a nova medição é considerada mais confiável.
    KalmanGainWall = oldVar / (oldVar + measureVariance)

    # Atualiza a estimativa do valor com base na medição atual e na estimativa anterior.
    estValueWall = oldMeasure + KalmanGainWall * (measure - oldMeasure)
    
    # Atualiza a incerteza da estimativa. A nova covariância é reduzida pelo ganho de Kalman, 
    # refletindo a maior confiança na nova estimativa.
    estCovarianceWall = (1 - KalmanGainWall) * oldVar

    return [estValueWall, estCovarianceWall, KalmanGainWall]


class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()


        estValueWall = 0
        estCovarianceWall = 5
        kalmanGainWall = estCovarianceWall / (estCovarianceWall + measureVariance)

        num_iter = 0

        while True:
            self.readSensors()
           
            if self.measures.endLed:
                print(self.robName + " exiting")
                quit()

            if num_iter > 1000:
                print(f"Final Values:")            
                print(f"Wall Estimate: {estValueWall} | var: {estCovarianceWall} | gain: {kalmanGainWall}")
                quit()

            num_iter += 1

            estValueWall, estCovarianceWall, kalmanGainWall = kalmanFilter(self.measures.irSensor[0], estValueWall, estCovarianceWall, kalmanGainWall)

            if self.measures.irSensor[0] != 0:
                val = 1 / self.measures.irSensor[0]
            else:
                val = float('inf')  # ou algum valor padrão, ou trate o erro de forma diferente
                print("Warning: Sensor reading is zero, setting val to infinity.")

            print(f"Wall Measurement num {num_iter}: {val}")
            print(f"Estimate for {val}: {estValueWall}")



rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    rob.run()
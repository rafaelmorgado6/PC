import sys
from croblink import *
from math import *
import time

#  CHECK WHAT VALUE THIS SHOULD BE
measureVariance = 1

def kalmanFilter(measure, oldMeasure, oldVar, measureVariance):

    # Ganho de Kalman determina quanto da nova medição deve ser incorporada à estimativa anterior.
    # Um ganho maior significa que a nova medição é considerada mais confiável.
    KalmanGainComp = oldVar / (oldVar + measureVariance)

    # Atualiza a estimativa do valor com base na medição atual e na estimativa anterior.
    estValueComp = oldMeasure + KalmanGainComp * (measure - oldMeasure)
    
    # Atualiza a incerteza da estimativa. A nova covariância é reduzida pelo ganho de Kalman, 
    # refletindo a maior confiança na nova estimativa.
    estCovarianceComp = (1 - KalmanGainComp) * oldVar

    return [estValueComp, estCovarianceComp, KalmanGainComp]


class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()


        estValueComp = 0
        estCovarianceComp = 5
        kalmanGainComp = estCovarianceComp / (estCovarianceComp + measureVariance)

        num_iter = 0

        while True:
            self.readSensors()
           
            if self.measures.endLed:
                print(self.robName + " exiting")
                quit()

            if num_iter > 1000:
                print(f"Final Values:")            
                print(f"Compass Estimate: {estValueComp} | var: {estCovarianceComp} | gain: {kalmanGainComp}")
                quit()

            num_iter += 1

            estValueComp, estCovarianceComp, kalmanGainComp = kalmanFilter(self.measures.compass, estValueComp, estCovarianceComp, kalmanGainComp)

            print(f"Compass Measurement num {num_iter}: {self.measures.compass}")
            print(f"Estimate for {self.measures.compass}: {estValueComp}")



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

    #Compass Measurement num 1: 2.0
    #Estimate for 2.0: 1.7142857142857144
    '''O filtro de Kalman melhora a estimativa do robô, 
    levando em consideração a medição do sensor e a incerteza associada. 
    Neste caso, o robô leu um valor de 2.0, mas a estimativa ajustada é menor,
     em torno de 1.71, refletindo a incerteza na medição e a influência das medições anteriores.'''
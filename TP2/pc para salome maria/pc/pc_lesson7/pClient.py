import sys
from croblink import *
from math import *
import xml.etree.ElementTree as ET
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.setup_fuzzy()

    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap

    def printMap(self):
        for l in reversed(self.labMap):
            print(''.join([str(l) for l in l]))

    def run(self):
        if self.status != 0:
            print("Connection refused or error")
            quit()

        state = 'stop'
        stopped_state = 'run'

        while True:
            self.readSensors()

            if self.measures.endLed:
                print(self.robName + " exiting")
                quit()

            if state == 'stop' and self.measures.start:
                state = stopped_state

            if state != 'stop' and self.measures.stop:
                stopped_state = state
                state = 'stop'

            if state == 'run':
                if self.measures.visitingLed==True:
                    state='wait'
                if self.measures.ground==0:
                    self.setVisitingLed(True)
                self.wander()
            elif state=='wait':
                self.setReturningLed(True)
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    state='return'
                self.driveMotors(0.0,0.0)
            elif state=='return':
                if self.measures.visitingLed==True:
                    self.setVisitingLed(False)
                if self.measures.returningLed==True:
                    self.setReturningLed(False)
                self.wander()
            

    def wander(self):

        lowest_d = 26

        for sensor in self.measures.irSensor:
            lowest_d = sensor if lowest_d < sensor else lowest_d

        self.avoid_obstacles.input['distance'] = lowest_d
        self.avoid_obstacles.compute()
        print("lowest distance: " + str(lowest_d))
        print("linear_speed: " + str(self.avoid_obstacles.output['linear_speed']))
        print("angular speed: " + str(self.avoid_obstacles.output['angular_speed']))
        self.driveMotors(self.avoid_obstacles.output['linear_speed'] + self.avoid_obstacles.output['angular_speed'],
                         self.avoid_obstacles.output['linear_speed'])
                

    def setup_fuzzy(self):

        self.fuzzy_distance = ctrl.Antecedent(np.arange(0, 25, 0.1), 'distance') 
        self.fuzzy_linear_speed = ctrl.Consequent(np.arange(0, 0.15, 0.01), 'linear_speed')
        self.fuzzy_angular_speed = ctrl.Consequent(np.arange(0, 0.15, 0.01), 'angular_speed')  

        self.fuzzy_distance.automf(3)

        self.fuzzy_linear_speed['poor'] = fuzz.trimf(self.fuzzy_linear_speed.universe, [0, 0, 0.03])
        self.fuzzy_linear_speed['good'] = fuzz.trimf(self.fuzzy_linear_speed.universe, [0.03, 0.15, 0.15])
        self.fuzzy_angular_speed['poor'] = fuzz.trimf(self.fuzzy_angular_speed.universe, [0, 0, 0.03])
        self.fuzzy_angular_speed['good'] = fuzz.trimf(self.fuzzy_angular_speed.universe, [0.03, 0.15, 0.15])

        self.fuzzy_rules = []
        self.fuzzy_rules.append(ctrl.Rule(self.fuzzy_distance['poor'], self.fuzzy_linear_speed['poor']))
        self.fuzzy_rules.append(ctrl.Rule(self.fuzzy_distance['poor'], self.fuzzy_angular_speed['good']))
        self.fuzzy_rules.append(ctrl.Rule(self.fuzzy_distance['good'], self.fuzzy_linear_speed['good']))
        self.fuzzy_rules.append(ctrl.Rule(self.fuzzy_distance['good'], self.fuzzy_angular_speed['poor']))

        self.fuzzy_controller = ctrl.ControlSystem(self.fuzzy_rules)

        self.avoid_obstacles = ctrl.ControlSystemSimulation(self.fuzzy_controller)

class Map():
    def __init__(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        
        self.labMap = [[' '] * (CELLCOLS*2-1) for i in range(CELLROWS*2-1) ]
        i=1
        for child in root.iter('Row'):
           line=child.attrib['Pattern']
           row =int(child.attrib['Pos'])
           if row % 2 == 0:  # this line defines vertical lines
               for c in range(len(line)):
                   if (c+1) % 3 == 0:
                       if line[c] == '|':
                           self.labMap[row][(c+1)//3*2-1]='|'
                       else:
                           None
           else:  # this line defines horizontal lines
               for c in range(len(line)):
                   if c % 3 == 0:
                       if line[c] == '-':
                           self.labMap[row][c//3*2]='-'
                       else:
                           None
               
           i=i+1


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
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    rob=MyRob(rob_name,pos,[0.0,60.0,-60.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
    
    rob.run()

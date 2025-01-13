
import math
import xml.etree.ElementTree as ET
import numpy as np

from croblink import CRobLinkAngs
import sys


CELLROWS=7
CELLCOLS=14

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host, path_file):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.path_file = path_file
        self.out_r = 0
        self.out_l = 0
        self.x = 0
        self.y = 0

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

        self.readSensors()
        self.ini_gps_x = self.measures.x
        self.ini_gps_y = self.measures.y

        while not self.measures.start:
            self.readSensors()

        with open(self.path_file) as f:
            for line in f:
                pos =np.fromstring(line, dtype = float, sep=' ')
                print('pos',pos)
                self.goto(pos)

            self.finish()

    def goto(self, pos):
        dir_diff = self.measures.compass - np.arctan2(*reversed(pos-self.my_gps()))*180.0/np.pi
        while dir_diff > 180.0:
            dir_diff -= 360.0
        while dir_diff < -180.0:
            dir_diff += 360.0

        if np.fabs(dir_diff)<45.0:
            self.go2()
        else:
            if dir_diff > 0:
                self.rotate(-1)
            else:
                self.rotate( 1)
            self.goto(pos)

    def rotate(self, rot):  # rot: 1 - rotate left ; -1 - rotate right
        dir = (self.measures.compass + 360 + 45) // 90 % 4

        targetDir = dir + rot
        targetAngle = 180  # all angles will be tranformed so that target is at 180 and range is 0-359

        angle = (self.measures.compass+(-targetDir)*90+180+720) % 360

        while  abs(angle-targetAngle) > 10.0 :
            
            self.driveMotorsExt(-0.07*rot,0.07*rot)
            self.readSensors()

            angle = (self.measures.compass+(-targetDir)*90+180+720) % 360


    def go2(self):
        dir = (self.measures.compass + 360 + 45) // 90 % 4
        posVec = self.my_gps() 
        posInitVec = posVec
        dirVec = np.array([np.cos(dir * np.pi/2),np.sin(dir * np.pi/2)])

        targetLin = posVec + 2.0 * dirVec
        targetLin = np.round(targetLin)
        targetRot = targetLin + 0.5 * dirVec
        while (posVec-posInitVec).dot(dirVec) < (targetLin-posInitVec).dot(dirVec)-0.1:
            errDir = self.measures.compass - np.arctan2(*(targetRot-posVec)[::-1])*180.0/np.pi
            if errDir>180.0:
                errDir = errDir - 360
            elif errDir < -180.0:
                errDir = errDir + 360

            self.readSensors()
            self.driveMotorsExt(0.1+0.005*errDir,0.1-0.005*errDir)
            
            posVec = self.my_gps() 

    def my_gps(self):
        return np.array([self.x, self.y])

    def driveMotorsExt(self, in_l, in_r):

        self.driveMotors(in_l, in_r)

        self.out_r = ((in_r + self.out_r)/2)
        self.out_l = ((in_l + self.out_l)/2)

        lin = (self.out_r + self.out_l)/2

        self.x = self.x + lin*math.cos(self.measures.compass*math.pi/180)
        self.y = self.y + lin*math.sin(self.measures.compass*math.pi/180)

        self.sensor_walls_robot()

        dir = (self.measures.compass + 360 + 45) // 90 % 4
        y_pos = []
        x_pos = []
        for sensor, has_wall in self.walls_detected_robot.items():
            if has_wall:
                d = 1/self.measures.irSensor[int(sensor)]
                if dir%2 == 0:
                    y = round(self.y)
                    if dir == 0:
                        if sensor == '2':
                            y_pos.append(y-(0.4-d))
                        if sensor == '1':
                            y_pos.append(y+(0.4-d))
                    if dir == 2:
                        if sensor == '2':
                             y_pos.append(y+(0.4-d))
                        if sensor == '1':
                             y_pos.append(y-(0.4-d))
                else:  
                    x = round(self.x)
                    if dir == 1:
                        if sensor == '2':
                            x_pos.append(x+(0.4-d))
                        if sensor == '1':
                            x_pos.append(x-(0.4-d))
                    if dir == 3:
                        if sensor == '2':
                            x_pos.append(x-(0.4-d))
                        if sensor == '1':
                            x_pos.append(x+(0.4-d))

        if len(x_pos) > 0:
            self.x = sum(x_pos)/len(x_pos)
        if len(y_pos) > 0:
            self.y = sum(y_pos)/len(y_pos)


    def predict_walls(self):

        predicted_x = round(self.x/2)
        predicted_y = round(self.y/2)
    
        map_y = int(ini_line)*2+predicted_y*2
        map_x = int(ini_col)*2+predicted_x*2

        possible_walls = [(1,0),(0,1),(-1,0),(0,-1)]
        self.walls_excepted = []
        for w in possible_walls:
            if self.labMap[map_y+w[1]][map_x+w[0]] != ' ' and self.labMap[map_y+w[1]][map_x+w[0]] != 'p':
                self.walls_excepted.append(w)

        self.walls_excepted.sort()

    def sensor_walls_map(self):

        measures = []
        for _ in range(10):
            #self.readSensors()
            measures.append(self.measures.irSensor)

        average_measures = np.sum(measures,axis=0)/len(measures)

        self.walls_detected = []
        if average_measures[0] > 1.25:
            self.walls_detected.append((1,0))
        if average_measures[1] > 1.25:
            self.walls_detected.append((0,1))
        if average_measures[2] > 1.25:
            self.walls_detected.append((0,-1))
        if average_measures[3] > 1.25:
            self.walls_detected.append((-1,0))
                
        if self.measures.compass > 45 and self.measures.compass <= 135:
            self.walls_detected = self.rotate_walls(self.walls_detected, math.pi/2)
        elif self.measures.compass > 135 and self.measures.compass <= 225:
            self.walls_detected = self.rotate_walls(self.walls_detected, math.pi)
        elif self.measures.compass > 225 and self.measures.compass <= 315:
            self.walls_detected = self.rotate_walls(self.walls_detected, -math.pi/2)

        self.walls_detected.sort()


    def rotate_walls(self, walls, a):
        new_walls = []
        for w in walls:
            qx = math.cos(a) * w[0] - math.sin(a) * w[1]
            qy = math.sin(a) * w[0] + math.cos(a) * w[1]
            new_walls.append((round(qx),round(qy)))

        return new_walls

    def sensor_walls_robot(self):
        self.predict_walls()
        self.sensor_walls_map()

        excepted_set = set(self.walls_excepted)
        detected_set = set(self.walls_detected)
        filtered_walls = list(excepted_set.intersection(detected_set))

        dir = (self.measures.compass + 360 + 45) // 90 % 4
        self.walls_detected_robot = {'0': False, '1': False, '2': False, '3': False}

        direction_mapping = {
            0: {'0': (1, 0), '1': (0, 1), '3': (-1, 0), '2': (0, -1)},
            1: {'0': (0, 1), '1': (-1, 0), '3': (0, -1), '2': (1, 0)},
            2: {'0': (-1, 0), '1': (0, -1), '3': (1, 0), '2': (0, 1)},
            3: {'0': (0, -1), '1': (1, 0), '3': (0, 1), '2': (-1, 0)}
        }

        for w in self.walls_excepted:
            for sensor, direction in direction_mapping[dir].items():
                if w == direction:
                    self.walls_detected_robot[sensor] = True


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

ir_ang = np.array([0, math.pi/2, -math.pi/2, math.pi])
ir_pos = np.array([[np.cos(a), np.sin(a)] for a in ir_ang])*0.5

rob_name = "pClient1"
host = "localhost"
pos = 1
mapc = None
path_file = 'path.txt'
ini_line = 3
ini_col = 2

for i in range(1, len(sys.argv),2):
    if (sys.argv[i] == "--host" or sys.argv[i] == "-h") and i != len(sys.argv) - 1:
        host = sys.argv[i + 1]
    elif (sys.argv[i] == "--pos" or sys.argv[i] == "-p") and i != len(sys.argv) - 1:
        pos = int(sys.argv[i + 1])
    elif (sys.argv[i] == "--robname" or sys.argv[i] == "-r") and i != len(sys.argv) - 1:
        rob_name = sys.argv[i + 1]
    elif (sys.argv[i] == "--map" or sys.argv[i] == "-m") and i != len(sys.argv) - 1:
        mapc = Map(sys.argv[i + 1])
    elif (sys.argv[i] == "--xy" or sys.argv[i] == "-x") and i != len(sys.argv) - 1:
        path_file = sys.argv[i + 1]
    elif (sys.argv[i] == "--cell" or sys.argv[i] == "-c") and i != len(sys.argv) - 1:
        ini_line,ini_col = sys.argv[i + 1].split(sep='x')
        print('starting at line',ini_line,'column',ini_col)
    else:
        print("Unkown argument", sys.argv[i])
        quit()

if __name__ == '__main__':
    print('pClientXY v0.1, 2023')
    rob=MyRob(rob_name, pos, ir_ang * 180 / math.pi, host, path_file)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()

    rob.run()

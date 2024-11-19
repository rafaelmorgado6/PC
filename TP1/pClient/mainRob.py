
# python3 mainRob.py -m ../Labs/PathFinder/pathFinderDefault_lab.xml

import sys
from colorama import Fore, Style, init
import numpy as np
from croblink import *
from math import *
import xml.etree.ElementTree as ET

CELLROWS=7
CELLCOLS=14
drive_count = 0
move = 0

class MyRob(CRobLinkAngs):
    def __init__(self, rob_name, rob_id, angles, host):
        CRobLinkAngs.__init__(self, rob_name, rob_id, angles, host)
        self.labMap = None
        self.expected_measures = {} # inicializado como um dicionário vazio
        self.prob_matrix = np.full((CELLROWS, CELLCOLS), 0.01) # Inicializa matriz com 0.1
        
        self.in_left = 0.1
        self.in_right = 0.1   
        self.out_left = 0.0  
        self.out_right = 0.0 
        self.x = 0.0  # Posição inicial no eixo X
        self.y = 0.0  # Posição inicial no eixo Y
        self.theta = 0.0  # Orientação inicial (rad)

    # In this map the center of cell (i,j), (i in 0..6, j in 0..13) is mapped to labMap[i*2][j*2].
    # to know if there is a wall on top of cell(i,j) (i in 0..5), check if the value of labMap[i*2+1][j*2] is space or not
    def setMap(self, labMap):
        self.labMap = labMap
        self.expected_measures = self.calculate_expected_measures(CELLROWS, CELLCOLS)

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
                    self.setVisitingLed(True);
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

#################################################################################################
    
    def show_expected_measures(self):
        
        print("Expected measures:")
        for cell, measures in self.expected_measures.items():
            print(f"Célula {cell}:")
            print(f"  Above: {measures['above']:.2f}")
            print(f"  Below: {measures['below']:.2f}")
            print(f"  Left: {measures['left']:.2f}")
            print(f"  Right: {measures['right']:.2f}\n")


    def movement_model(self, in_left, in_right, noise=1):
        
        # Suaviza a entrada usando um filtro IIR
        self.out_left = ((in_left + self.out_left) / 2) * noise
        self.out_right = ((in_right + self.out_right) / 2) * noise

        # Calcula o deslocamento linear (média dos motores)
        lin = (self.out_left + self.out_right) / 2

        # Calcula a rotação (diferença dos motores dividido pelo diâmetro do robô)
        robotDiam = 1  
        rot = (self.out_right - self.out_left) / robotDiam

        # Atualiza posição e orientação
        theta_next = self.theta + rot
        x_next = self.x + lin * cos(self.theta)
        y_next = self.y + lin * sin(self.theta)

        # Atualiza as variáveis so self
        self.theta = theta_next
        self.x = x_next
        self.y = y_next

        return x_next, y_next, theta_next


    def print_probability_matrix(self):
    
        print("Matriz de Probabilidade:")
        for i in range(CELLROWS - 1, -1, -1):  # Exibe de baixo para cima
            row = []
            for j in range(CELLCOLS):
                value = self.prob_matrix[i, j]
                # Determina a cor com base no valor
                if value <= 0.01:
                    colored_value = f"{Style.RESET_ALL}{value:.2f}"  # Vermelho
                elif 0.01 < value <= 0.24:
                    colored_value = f"{Fore.RED}{value:.2f}{Style.RESET_ALL}"  # Vermelho
                elif 0.24 < value <= 0.5:
                    colored_value = f"{Fore.YELLOW}{value:.2f}{Style.RESET_ALL}"  # Amarelo
                else:
                    colored_value = f"{Fore.GREEN}{value:.2f}{Style.RESET_ALL}"  # Verde
                row.append(colored_value)
            # Exibe a linha da matriz com os valores coloridos
            print(" ".join(row))


    def save_probability_matrix(self, filename="localization.out"):
        with open(filename, "a") as file:
            for i in range(CELLROWS-1,-1,-1):
                # Formata cada linha da matriz como uma string com 2 casas decimais
                row = " ".join(f"{self.prob_matrix[i, j]:.2f}" for j in range(CELLCOLS))
                file.write(row + "\n")
            file.write("\n")  # Adiciona uma linha em branco para separar atualizações


    def move(self):
        
        # Cria uma nova matriz para armazenar a atualização
        new_prob_matrix = np.zeros_like(self.prob_matrix)

        # Itera por cada célula na matriz de probabilidade
        for i in range(CELLROWS):
            for j in range(CELLCOLS):
                # Guarda prob da celula (i,j)
                prob = self.prob_matrix[i, j]

                # Movimento para a direita
                if j < CELLCOLS - 1:  # Verifica se não está na borda direita
                    new_prob_matrix[i, j + 1] += prob 
                else:  # Caso esteja na borda direita, mantém-se na mesma posição
                    new_prob_matrix[i, j] += prob 

        # Normaliza a matriz de probabilidade para garantir que a soma seja 1
        self.prob_matrix = new_prob_matrix / np.sum(new_prob_matrix)


    def sense(self, sensor_data, std_dev=0.1):

        new_prob_matrix = np.zeros_like(self.prob_matrix)

        # Itera sobre cada célula na matriz de probabilidade
        for i in range(CELLROWS):
            for j in range(CELLCOLS):

                # Guarda prob da celula (i,j)
                prob = self.prob_matrix[i, j]

                match = 1 # Inicializa o fator de correspondência para esta célula

                # Itera sobre as direções (above, below, right, left) 
                # e os valores medidos pelos sensores para essas direções.
                for direction, sensor_value in sensor_data.items():
                    
                    expected_value = self.expected_measures[(i, j)][direction] #> 1.0  # assume-se True para valores acima de 1.0
                    
                    variance = std_dev ** 2
                    coef = 1 / np.sqrt(2 * np.pi * variance)  # Coeficiente de normalização
                    expo = np.exp(-((sensor_value - expected_value) ** 2) / (2 * variance))  # Termo exponencial
                    gauss = coef*expo
                    match *= gauss
                        
                # Ajusta a probabilidade da célula com base na correspondência
                new_prob_matrix[i, j] = prob * match
                #print(f"Célula ({i},{j}): Probabilidade Inicial: {prob:.4f}, Match: {match:.4f}, Probabilidade Ajustada: {new_prob_matrix[i, j]:.4f}")

        # Normaliza para que a soma das probabilidades seja 1
        total_sum = np.sum(new_prob_matrix)
        self.prob_matrix = new_prob_matrix / total_sum

        #print(f"Soma Total após Normalização: {np.sum(self.prob_matrix):.4f}")


    def there_is_wall_above(self, i, j):
        # Multiplicamos i por 2 e verificamos logo acima (i*2 + 1)
        if (i * 2 + 1) < len(self.labMap):
            if self.labMap[i * 2 + 1][j * 2] == '-':   # True/False
                return True
        return False

    def there_is_wall_below(self, i, j):
        # Multiplicamos i por 2 e verificamos logo abaixo (i*2 - 1)
        if (i * 2 - 1) >= 0:
            if self.labMap[i * 2 - 1][j * 2] == '-':
                return True
        return False

    def there_is_wall_left(self, i, j):
        # Multiplicamos j por 2 e verificamos logo à esquerda (j*2 - 1)
        if (j * 2 - 1) >= 0:
            if self.labMap[i * 2][j * 2 - 1] == '|':    
                return True
        return False

    def there_is_wall_right(self, i, j):
        # Multiplicamos j por 2 e verificamos logo à direita (j*2 + 1)
        if (j * 2 + 1) < len(self.labMap[0]):
            if self.labMap[i * 2][j * 2 + 1] == '|':
                return True
        return False


    def calculate_expected_measures(self, rows, cols):
        expected_measures = {}

        # (i,j) -> (linhas,colunas)
        for i in range(rows):
            for j in range(cols):
                
                # Células internas
                above = 2.5 if self.there_is_wall_above(i, j) else 0.4
                below = 2.5 if self.there_is_wall_below(i, j) else 0.4
                left  = 2.5 if self.there_is_wall_left(i, j) else 0.4
                right = 2.5 if self.there_is_wall_right(i, j) else 0.4

                # Cantos:
                if i == 0 and j == 0:  # Canto inferior esquerdo
                    below = 2
                    left = 2
                elif i == 6 and j == 0:  # Canto superior esquerdo
                    above = 2
                    left = 2
                elif i == 0 and j == 13:  # Canto inferior direito
                    below = 2
                    right = 2
                elif i == 6 and j == 13:  # Canto superior direito
                    above = 2
                    right = 2
                
                # Bordas:
                elif i == 0 and (j != 0 and j != 13):  # Borda inferior
                    below = 2
                elif i == 6 and (j != 0 and j != 13):  # Borda superior
                    above = 2
                elif j == 0 and (i != 0 and i != 13):  # Borda esquerda
                    left = 2
                elif j == 13 and (i != 0 and i != 13):  # Borda direita
                    right = 2
                    
                expected_measures[(i, j)] = {
                    'above': above,
                    'below': below,
                    'left': left,
                    'right': right
                }
                #print(f"Medidas para célula ({i},{j}): {expected_measures[(i, j)]}")

        return expected_measures


    def wander(self):
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
        
        global drive_count
        global move

        
        # Somente exibir o print a cada 20 chamadas
        if drive_count % 20 == 0:
            print("\n________________________________________________________________________________\n")
            print("move " + str(move))
            print("\nLeft: " + str(self.measures.irSensor[left_id]))
            print("Right: " + str(self.measures.irSensor[right_id]))
            print("Back: " + str(self.measures.irSensor[back_id]))
            print("Center: " + str(self.measures.irSensor[center_id]) + "\n")
            move += 1

            

            # Usa as measures dos sensores para calcular sense
            sensor_data = {
                "right": self.measures.irSensor[center_id] ,
                "below": self.measures.irSensor[right_id ] ,
                "above": self.measures.irSensor[ left_id ] ,
                "left" : self.measures.irSensor[ back_id ] }

            self.sense(sensor_data)

            # Imprime a matriz probabilidade
            self.print_probability_matrix()

            # Guarda a matriz no ficheiro 'localization'.out'
            self.save_probability_matrix()

            # Só fazemos move aqui pois há a probabilidade de ele começar em j=0
            self.move()    
        
            # Estima a próxima posição usando movement_model
            x_next, y_next, theta_next = self.movement_model(self.in_left, self.in_right)

            # Exibe a estimativa da próxima posição
            print(f"\nPróxima posição estimada: x={x_next:.2f}, y={y_next:.2f}, θ={theta_next:.2f} rad")
            
        self.driveMotors(self.in_left, self.in_right)
    
        # Incrementar o contador a cada chamada de wander
        drive_count += 1
        
        # Termina caso bata numa parede
        if (self.measures.irSensor[center_id] or self.measures.irSensor[right_id] or self.measures.irSensor[left_id] or self.measures.irSensor[back_id]) > 10:
            exit()

##############################################################################################################
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
    open("localization.out", "w").close()
    rob=MyRob(rob_name,pos,[0.0,90.0,-90.0,180.0],host)
    if mapc != None:
        rob.setMap(mapc.labMap)
        rob.printMap()
        rob.show_expected_measures()  # Exibe as expected measures antes de começar a andar
        rob.print_probability_matrix()
    rob.run()
# 4_localization_2d.py: develop functions sense() and move()

colors = [['red', 'green', 'green', 'red' , 'red'],
          ['red', 'red', 'green', 'red', 'red'],
          ['red', 'red', 'green', 'green', 'red'],
          ['red', 'red', 'red', 'red', 'red']]

measurements = ['green']                                        # test 1
#motions is a list of 2d lists. each 2d list represents first movement in x (columns in colors) then in y (lines in colors)
motions = [[1,0]]                                               # test 1
#measurements = ['green', 'red', 'red' ,'green', 'red','red']    # test 2
#motions = [[1,0],[0,0],[0,1],[0,1],[-1,0],[0,0]]   # (x,y)      # test 2

sensor_right = {}
sensor_right['green'] = 0.8
sensor_right['red'] = 0.7

p_move = 1.0

def show(p):
    for i in range(len(p)):
        print(p[i])

def sense(p, Z):
    q = []  # vai armazenar as novas probabilidades
    sum_q = 0
    
    for i in range(len(colors)): # len = 5
        q_row = []
        for j in range(len(p[i])):
            hit = (Z == colors[i][j])  # se Z('green') = à cor lida, devolve 'True'
            #print(hit) F T T F F 
        
            if hit:
                prob = ( sensor_right[colors[i][j]]*p[i][j] ) # P(Z|X)*P(X)
            else:
                prob = ( (1-sensor_right[colors[i][j]])*p[i][j]) # 1-P(Z|X)*P(X)
            # q.append( hit*sensor_right[colors[s]]*p[s] + (1-hit)*(1-sensor_right[colors[s]])*p[s])

            q_row.append(prob)
            sum_q += prob     

            q.append(q_row)  # Adiciona a linha completa a q

    for i in range(len(q)):
        for j in range(len(q[i])):
            q[i][j] /= sum_q  # Normaliza a célula correspondente
    return q

def move(p, U):
    height = len(p)
    width = len(p[0])
    q = [[0.0 for _ in range(width)] for _ in range(height)]
    
    for i in range(height):
        for j in range(width):
            from_i = (i - U[1]) % height
            from_j = (j - U[0]) % width
            q[i][j] = p_move * p[from_i][from_j] + (1 - p_move) * p[i][j]
    return q

height = len(colors)
width  = len(colors[0])

n = height * width

p = [[1.0 / n for _ in range(width)] for _ in range(height)]
for l in range(height):
    q=[]
    for c in range(width):
        q.append(1./n)
    p.append(q)

for s in range(len(measurements)):
    print("sense ",measurements[s])
    p = sense(p,measurements[s])
    show(p)
    print("move ", motions[s])
    p = move(p,motions[s])
    show(p)



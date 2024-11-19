# 3_localization_1d.py: develop functions sense() and move()

colors = ['red', 'green', 'green', 'red' , 'red']

#measurements = ['green']                                            # test 1
#motions = [[1]]                                                     # test 1
measurements = ['green', 'green', 'green' ,'green', 'green','red']  # test 2
motions = [[1],[0],[-1],[1],[1],[0]]                                # test 2

sensor_right = {}
sensor_right['green'] = 0.6
sensor_right['red'] = 0.8

p_move = 0.8

def sense(p, Z):
    q = []  # vai armazenar as novas probabilidades
    sum = 0
    
    for s in range(len(colors)): # len = 5
        hit = (Z == colors[s])  # se Z('green') = à cor lida, devolve 'True'
        #print(hit) F T T F F 
        
        if hit:
           q.append( sensor_right[colors[s]]*p[s] ) # P(Z|X)*P(X)
        else:
           q.append( (1-sensor_right[colors[s]])*p[s]) # 1-P(Z|X)*P(X)
        # q.append( hit*sensor_right[colors[s]]*p[s] + (1-hit)*(1-sensor_right[colors[s]])*p[s])
        
        sum += q[s] # q[s]-> p(0.2)*sensor_right['green'(0.6)/'red(0.8)]
       
    for s in range(len(colors)):
       
        # q[s] = [0.04 0.12 0.12 0.04 0.04] sum = 0.36 
        q[s] = q[s]/sum
    
    return q

def move(p, U):
    q = []  # vai armazenar as novas probabilidades

    for c in range(len(p)): # len = 5
            
            # Movimento bem-sucedido + Ficar na mesma posição
            s = p_move * p[(c-U[0]) % len(p)] + (1-p_move) * p[c]
            
            q.append(s)
    return q

#main
p = []

width  = len(colors)
n = width

for c in range(width):
    p.append(1./n)

for s in range(len(measurements)):
    print("sense ",measurements[s])
    p = sense(p,measurements[s])
    print(p)
    print("move ", motions[s])
    p = move(p,motions[s])
    print(p)



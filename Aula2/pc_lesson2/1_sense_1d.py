# 1_sense_1d.py: develop function sense(p, Z) to update belief p after measuring Z

colors = ['red', 'green', 'green', 'red' , 'red']

measurements = ['green']                                       # test 1
#measurements = ['green', 'green', 'green' ,'green', 'green']   # test 2

sensor_right = {}
sensor_right['green'] = 0.6 # o sensor está certo 60% das vezes quando detecta 'green'
sensor_right['red'] = 0.8   # o sensor está certo 80% das vezes quando detecta 'red'


def sense(p, Z): # p = [0.2 0.2 0.2 0.2 0.2], Z recebe green  
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

#main
p = []

width  = len(colors) # len = 5

for c in range(width):
    p.append(1./width) # 0.2

for s in range(len(measurements)): # len = 1 ou len = 5
    p = sense(p,measurements[s])

print(p)


import random

colors = ['red', 'green', 'green', 'red' , 'red']

measurements = ['green']                                            # test 1
motions = [[1]]                                                     # test 1
#measurements = ['green', 'green', 'green' ,'green', 'green','red']  # test 2
#motions = [[1],[0],[-1],[1],[1],[0]]                                # test 2

sensor_right = {}
sensor_right['green'] = 0.6
sensor_right['red'] = 0.8

p_move = 0.8

def move(p, U): # p = [0.5 0.5 0 0 0]   U = 1(move right)
    """Update p after movement U"""

    newParticleSet = []

    for particle in p:

#  Se o random for menor que p_move, a partícula se move para a direita de acordo com o valor de U
        if random.random() < p_move:
            newParticle = (particle + U[0]) % len(colors)

#  Caso contrário, a partícula permanece na mesma posição.
        else:
            newParticle = particle

        newParticleSet.append(newParticle)

    return newParticleSet

#main
p = []

width  = len(colors)
n = width

# p = [0.5, 0.2, 0.1, 0.1, 0.1]             #  OLD Bayes
p = [0, 0, 0, 1, 1, 2, 2, 2, 2, 3, 4, 4]  #  New particles
#p = [0, 1, 2]
print(p)
#p = [round(random.random() * 4, 0) for _ in range(0, 5)]

for s in range(len(measurements)):
    print("move ", motions[s])
    p = move(p, motions[s])
    print(p)
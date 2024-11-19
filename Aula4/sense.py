import random

colors = ['red', 'green', 'green', 'red' , 'red']

measurements = ['green']                                       

sensor_right = {}
sensor_right['green'] = 0.6 
sensor_right['red'] = 0.8   

def sense(p, Z):

    #  Associate it with the weight, that comes from the sensor model
    #  Example: sees green: P(Gm|Gc) = 0.6, P(Gm|Rc) = 0.2

    #  Then resample to get the new particle set
    #  Get the weights and uniform distribution
    #  Sample [0, 1] uniformally

    newParticleSet = []
    sumOfWeights = 0

    for particle in p:
        partColour = colors[particle]

        partWeight = abs((partColour != Z) - sensor_right[partColour])

        newParticleSet.append((particle, sumOfWeights))
        sumOfWeights += partWeight

    finalParticleSet = []

    for i in range(0, len(newParticleSet)):

        r = random.random() * (sumOfWeights - partWeight)

        newPartID = 0
        currWeightSum = 0

        while r > newParticleSet[newPartID][1]:
            newPartID += 1

        finalParticleSet.append(newParticleSet[newPartID][0])



    finalParticleSet.sort()

    return finalParticleSet

p = []

width  = len(colors)
n = width

#for c in range(width):
#    p.append(1./n)
#    print(p)

# p = [0.5, 0.2, 0.1, 0.1, 0.1]             #  OLD Bayes
p = [0, 0, 0, 1, 1, 2, 2, 2, 2, 3, 4, 4]  #  New particles
#p = [0, 1, 2]
print(p)
#p = [round(random.random() * 4, 0) for _ in range(0, 5)]

for s in range(len(measurements)):
    print("sense ",measurements[s])
    p = sense(p,measurements[s])
    print(p)
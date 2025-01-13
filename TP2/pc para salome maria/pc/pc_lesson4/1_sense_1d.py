import numpy as np

colors = ['red', 'green', 'green', 'red' , 'red']

measurements = ['green']                                       # test 1
#measurements = ['green', 'green', 'green' ,'green', 'green']   # test 2

sensor_right = {}
sensor_right['green'] = 0.6
sensor_right['red'] = 0.8


def sense(p, Z):
    """Update belief array p according to new measurement Z"""

    Wacc = []
    temp = []

    for i in range(len(p)):
        if colors[p[i]] == Z:
            if i == 0:
                Wacc.append(sensor_right[Z])
            else:
                Wacc.append(sensor_right[Z] + Wacc[i-1])
        else:
            if i == 0:
                Wacc.append(1-sensor_right[Z])
            else:
                Wacc.append(1-sensor_right[Z] + Wacc[i-1])

    for i in range(len(p)):
        r = np.random.uniform(0,Wacc[-1])
        h = 0
        while r > Wacc[h]:
            h += 1
        temp.append(p[h])
    temp.sort()

    return temp

#main
p = []

width  = len(colors)
n = width

particles = 10

for i in range(width):
    p.extend([i] * int(particles/width))

print(p)

for s in range(len(measurements)):
    p = sense(p,measurements[s])

print(p)


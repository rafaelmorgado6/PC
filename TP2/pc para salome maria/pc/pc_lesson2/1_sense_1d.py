colors = ['red', 'green', 'green', 'red' , 'red']

measurements = ['green']                                       # test 1
#measurements = ['green', 'green', 'green' ,'green', 'green']   # test 2

sensor_right = {}
sensor_right['green'] = 0.6
sensor_right['red'] = 0.8


def sense(p, Z):
    """Update belief array p according to new measurement Z"""

    for i in range(len(p)):
        if colors[i] == Z:
            p[i] *= sensor_right[Z]
        else:
            p[i] *= (1-sensor_right[colors[i]])

    #n = 1/sum(p)

    #for i in range(len(p)):
    #    p[i] *= n

    return p

#main
p = []

width  = len(colors)
n = width

for c in range(width):
    p.append(1./n)
print(p)

for s in range(len(measurements)):
    p = sense(p,measurements[s])

print(p)


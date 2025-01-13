import random
colors = ['red', 'green', 'green', 'red' , 'red']

motions = [[1]]                      # test 1
#motions = [[1],[0],[-1],[1],[0]]     # test 2

p_move = 0.8

def move(p, U):
    """Update p after movement U"""
    new_p = []
    for i in range(len(p)):
        sample = random.uniform(0,1)
        if U == [1]:
            if sample < 0.8:
                if(i == (len(p)-1)):
                    new_p.append(0)
                else:
                    new_p.append(p[i] + 1)
            else:
                new_p.append(p[i])
        else:
            if sample < 0.8:
                if(i == 0):
                    new_p.append(p[len(p)-1])
                else:
                    new_p.append(p[i] - 1)
            else:
                new_p.append(p[i])
    
    new_p.sort()




    return new_p

#main
p = [0, 0, 0, 0, 0, 1,1,1,3,4]

width  = len(colors)
n = width
p_number = 10 #total number of particles
cell_number = int(p_number/width)  #number of particles in each cell

print(p)

#for c in range(width):
    #for i in range(cell_number):
        #p.append(c)

for s in range(len(motions)):
    p = move(p,motions[s])

print(p)


colors = ['red', 'green', 'green', 'red' , 'red']

motions = [[1]]                      # test 1
#motions = [[1],[0],[-1],[1],[0]]     # test 2

p_move = 0.8

def move(p, U):
    """Update p after movement U"""
    #TODO: insert your code here
    newp = []
    if(U == [1]):
        for i in range(len(p)):
            if i == 0:
                newp.append(p[i]*0.2)
            else:
                newp.append(p[i-1]*0.8 + p[i]*0.2)
    elif(U==[0]):
        for i in range(len(p)):
            if i == 0:
                newp.append(p[i]*0.2 + p[i+1]*0.8)
            elif i == 4:
                newp.append(p[i]*0.2 + p[i-1]*0.8)
            else:
                newp.append(p[i]*0.2 + p[i-1]*0.8 + p[i+1]*0.8)
    elif(U==[-1]):
        for i in range(len(p)):
            if(i==4):
                newp.append(p[i]*0.2)
            else:
                newp.append(p[i]*0.2 + p[i+1]*0.8)

    return newp

#main
p = [0.5, 0.5, 0, 0, 0]

width  = len(colors)
n = width

for s in range(len(motions)):
    p = move(p,motions[s])

print(p)


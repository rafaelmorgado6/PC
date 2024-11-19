# 2_motion_1d.py: develop function move(p, U) to update belief p after action U

colors = ['red', 'green', 'green', 'red' , 'red']

#motions = [[1]]                      # test 1     -1 move left    0 stay  1 move right
motions = [[1],[0],[-1],[1],[0]]     # test 2

p_move = 0.8    # probabilidade de que o movimento seja bem-sucedido

def move(p, U): # p = [0.5 0.5 0 0 0]   U = 1(move right)
    q = []  # vai armazenar as novas probabilidades

    for c in range(len(p)): # len = 5
            
            # Movimento bem-sucedido + Ficar na mesma posição
            s = p_move * p[(c-U[0]) % len(p)] + (1-p_move) * p[c]
            
            q.append(s)
    return q

#main
p = [0.5, 0.5, 0, 0, 0]

width  = len(colors)

for s in range(len(motions)):
    p = move(p,motions[s])

print(p)


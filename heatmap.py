import numpy as np
import operator
import time
import random
import matplotlib.pyplot as plt
from  matplotlib.tri import Triangulation

# Heatmap
# q_values_block = q_values[0]
# q_values_no_block = q_values[1]
q_values_block =[np.array([[ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
       [ 0.15878774, -0.35746083, -0.76217311, -0.77389077, -0.78594769],
       [-0.5654671 , -0.55987333, -0.91900529, -0.85010975, -0.83068745],
       [-0.80628852, -0.89230762, -0.60958794, -0.76217311, -0.85760426],
       [-0.82517539, -0.83972447, -0.72154957, -0.60278568, -0.98536141]]), np.array([[-0.55563839, -0.3016627 , -0.48665792, -0.69113501,  0.        ],
       [-0.26490811, -0.43119991, -0.74965591, -0.77380563,  0.        ],
       [-0.57448044, -0.44547244, -0.91900529, -0.85010975,  0.        ],
       [-0.81551472, -0.89612572, -0.67646646, -0.76075083,  0.        ],
       [-0.82517539, -0.83391662, -0.71985825, -0.59536538,  0.        ]]), np.array([[-0.79790013, -0.3016627 , -0.48665792, -0.69264313, -0.9537655 ],
       [-0.26490811, -0.43097364, -0.77797022, -0.76217311, -0.79609317],
       [-0.58187966, -0.55725752, -0.91670766, -0.85010975, -0.91134544],
       [-0.80628852, -0.89532605, -0.67646646, -0.75226682, -0.38707947],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ]]), np.array([[ 0.        ,  1.83217378, -0.37780125, -0.69264313, -0.98446537],
       [ 0.        , -0.44041026, -0.76217311, -0.76217311, -0.79609317],
       [ 0.        , -0.55987333, -0.91711759, -0.80993837, -0.91025517],
       [ 0.        , -0.89532605, -0.67126644, -0.75919823, -0.85760426],
       [ 0.        , -0.84222079, -0.70801098, -0.58187966, -0.98537242]])]
q_values_no_block = [np.array([[ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ],
       [-0.53670877, -0.22621906, -0.3016627 , -0.22621906, -0.05      ],
       [-0.18549375, -0.40480241, -0.26490811, -0.22621906, -0.44186589],
       [-0.0975    , -0.51449792, -0.16095023, -0.142625  ,  7.55435686],
       [-0.32992261,  0.14048328, -0.18549375, -0.26490811,  1.07772021]]), np.array([[-0.87791345, -0.58187966, -0.43119991, -0.36975059,  0.        ],
       [-0.53422249, -0.22621906, -0.3016627 , -0.22738256,  0.        ],
       [-0.07510506, -0.40366799, -0.26490811, -0.22253407,  0.        ],
       [ 0.1279775 , -0.52079637, -0.1832339 ,  0.22132887,  0.        ],
       [-0.32686834, -0.18549375, -0.18549375, -0.3016627 ,  0.        ]]), np.array([[-0.87791345, -0.5826924 , -0.43119991, -0.40126306,  1.34461711],
       [-0.55462063,  0.1830914 , -0.29892757, -0.26490811,  7.69813749],
       [-0.17989961, -0.43287372, -0.26014669, -0.22621906, -0.43003796],
       [-0.0975    , -0.5137907 , -0.142625  , -0.142625  , -0.0975    ],
       [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ]]), np.array([[ 0.        , -0.58187966, -0.43119991, -0.36975059, -0.45963991],
       [ 0.        , -0.22621906, -0.29097224, -0.26490811, -0.05      ],
       [ 0.        , -0.41071278,  0.10227813, -0.23104129, -0.45709076],
       [ 0.        , -0.51471683, -0.17764851, -0.142625  , -0.0975    ],
       [ 0.        , -0.18549375, -0.18549375, -0.22621906, -0.43119991]])]


# print("q values with block", q_values_block)
# print('q values without block', q_values_no_block)
# Functions for heatmap
def triangulation_for_triheatmap(M, N):
    xv, yv = np.meshgrid(np.arange(-0.5, M), np.arange(-0.5, N))  # vertices of the little squares
    xc, yc = np.meshgrid(np.arange(0, M), np.arange(0, N))  # centers of the little squares
    x = np.concatenate([xv.ravel(), xc.ravel()])
    y = np.concatenate([yv.ravel(), yc.ravel()])
    cstart = (M + 1) * (N + 1)  # indices of the centers

    trianglesN = [(i + j * (M + 1), i + 1 + j * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]
    trianglesE = [(i + 1 + j * (M + 1), i + 1 + (j + 1) * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]
    trianglesS = [(i + 1 + (j + 1) * (M + 1), i + (j + 1) * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]
    trianglesW = [(i + (j + 1) * (M + 1), i + j * (M + 1), cstart + i + j * M)
                  for j in range(N) for i in range(M)]

    return [Triangulation(x, y, triangles) for triangles in [trianglesN, trianglesE, trianglesS, trianglesW]]

M, N = 5,5
triangul = triangulation_for_triheatmap(M, N)

#plotting with block
values = q_values_block
cmaps = ['Blues', 'Greens', 'Purples', 'Reds']  # ['winter', 'spring', 'summer', 'autumn']
norms = [plt.Normalize(-0.5, 1) for _ in range(4)]
fig, ax = plt.subplots()

plt.title('Q table with block')
imgs = [ax.tripcolor(t, val.ravel(), cmap='RdYlGn',  vmin=-1, vmax=0, ec='white')
                for t, val in zip(triangul, values)]

for val, dir in zip(values, [(-1, 0), (0, 1), (1, 0), (0, -1)]):
    for i in range(M):
        for j in range(N):
            v = val[j][i]
            ax.text(i + 0.3 * dir[1], j + 0.3 * dir[0], f'{v:.2f}', color='k' if 0.2 < v < 0.8 else 'w', ha='center', va='center')

cbar = fig.colorbar(imgs[0], ax=ax)
ax.set_xticks(range(M))
ax.set_yticks(range(N))
ax.invert_yaxis()
ax.margins(x=0, y=0)
ax.set_aspect('equal', 'box')  # square cells

#without block
values = q_values_no_block
cmaps = ['Blues', 'Greens', 'Purples', 'Reds']  # ['winter', 'spring', 'summer', 'autumn']
norms = [plt.Normalize(-0.5, 1) for _ in range(4)]
fig, ax = plt.subplots()

imgs = [ax.tripcolor(t, val.ravel(), cmap='RdYlGn', vmin=-0.6, vmax=0.1, ec='white')
                for t, val in zip(triangul, values)]

plt.title('Q table without block')
for val, dir in zip(values, [(-1, 0), (0, 1), (1, 0), (0, -1)]):
    for i in range(M):
        for j in range(N):
            v = val[j][i]
            ax.text(i + 0.3 * dir[1], j + 0.3 * dir[0], f'{v:.2f}', color='k' if 0.2 < v < 0.8 else 'w', ha='center', va='center')

cbar = fig.colorbar(imgs[0], ax=ax)
ax.set_xticks(range(M))
ax.set_yticks(range(N))
ax.invert_yaxis()
ax.margins(x=0, y=0)
ax.set_aspect('equal', 'box')  # square cells

plt.show()
plt.tight_layout()
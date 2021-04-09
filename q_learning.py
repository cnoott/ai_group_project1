import numpy as np

class PDWorld():
    def __init__(self):
        self.width = 5
        self.height = 5

        '''
        self.R = n.matrix([[13,-1,-1,-1,13],
                           [-1,-1,-1,-1,-1],
                           [-1,-1,13,-1,13],
                           [-1,13,-1,-1,-1],
                           [-1,-1,-1,-1,13]])

        '''
        self.P = ((2,4), (3,1))
        self.D = ((0,0), (0,4), (2,2), (4,4))
        
        self.grid = np.matrix(np.zeros([self.width,self.height])) 



class Agent():
    def __init__(self, world, alpha, gamma): #world is a PDWorld object
        self.world = world
        self.Q = np.matrix(np.zeros([25,6]))

        self.alpha = alpha
        self.gamma = gamma

    def prandom(self, avaliable_actions):
        pass
        




import numpy as np

class PDWorld:
    def __init__(self):
        self.size = (5,5) #width and height
        '''
        self.R = n.matrix([[13,-1,-1,-1,13],
                           [-1,-1,-1,-1,-1],
                           [-1,-1,13,-1,13],
                           [-1,13,-1,-1,-1],
                           [-1,-1,-1,-1,13]])

        '''
        self.P = ((2,4), (3,1))
        self.D = ((0,0), (0,4), (2,2), (4,4))

        self.Q = np.matrix(np.zeros([10,5]))






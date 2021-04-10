import numpy as np
import operator


class PDWorld:
    def __init__(self):
        #Initialize PDWorld
        self.height = 5
        self.width = 5
        self.grid = np.zeros((self.height, self.width)) - 1

        self.initial_state = (4, 0, False)
        self.current_state = self.initial_state

        self.terminal_matrix = np.array([[2, 4, 0], [3, 1, 0], [0, 0, 4], [0, 4, 4], [2, 2, 4], [4, 4, 4]])
        self.initial_matrix = np.array([[2, 4, 8], [3, 1, 8], [0, 0, 0], [0, 4, 0], [2, 2, 0], [4, 4, 0]])
        self.current_matrix = self.initial_matrix

        # Set reward for Pickup/Dropoff states
        for i in range(np.shape(self.initial_matrix)[0]):
            self.grid[self.initial_matrix[i][0], self.initial_matrix[i][1]] = 13
        
        # Set available actions
        self.actions = ['N', 'S', 'W', 'E', 'P', 'D']

    # Show current state
    def get_current_state(self):
        grid = np.zeros((self.height, self.width))
        grid[self.current_state[0], self.current_state[1]] = 1
        print(np.concatenate((self.grid, grid), axis=1).astype(int))
    # 
    def get_reward(self, next_state)
        return self.grid[next_state]
    
       
import numpy as np
import operator


class PDWorld:
    def __init__(self):
        #Initialize PDWorld
        self.height = 5
        self.width = 5
        self.grid = np.zeros((self.height, self.width)) - 1
        self.terminal_states_reached = 0

        self.initial_state = (4, 0, False)
        self.current_state = list(self.initial_state)

        self.initial_matrix = np.array([[2, 4, 8], [3, 1, 8], [0, 0, 0], [0, 4, 0], [2, 2, 0], [4, 4, 0]])
        self.current_matrix = self.initial_matrix
        self.terminal_matrix = np.array([[2, 4, 0], [3, 1, 0], [0, 0, 4], [0, 4, 4], [2, 2, 4], [4, 4, 4]])

        # Set reward for Pickup/Dropoff states
        for i in range(np.shape(self.initial_matrix)[0]):
            self.grid[self.initial_matrix[i][0], self.initial_matrix[i][1]] = 13
        
        # Set available actions
        self.actions = ('N', 'S', 'W', 'E', 'P', 'D')

    # Show current state
    def print_current_state(self): # for debugging
        grid = np.zeros((self.height, self.width))
        grid[self.current_state[0], self.current_state[1]] = 1
        print(np.concatenate((self.grid, grid, self.current_matrix), axis=1).astype(int))
    
    def get_reward(self, state):
        return self.grid[state[0], state[1]]
    
    def take_action(self, action):
        
        if action == 'N':
            self.current_state = (self.current_state[0] - 1, self.current_state[1])
            reward = self.get_reward(self.current_state)

        elif action == 'S':
            self.current_state = (self.current_state[0] + 1, self.current_state[1])
            reward = self.get_reward(self.current_state)

        elif action == 'W':
            self.current_state = (self.current_state[0] - 1, self.current_state[1] - 1)
            reward = self.get_reward(self.current_state)
   
        elif action == 'E':
            self.current_state = (self.current_state[0] - 1, self.current_state[1] + 1)
            reward = self.get_reward(self.current_state)
        
        elif action == 'P':
            row = np.where((self.current_matrix[:,0:2]== self.current_state[0:2]).all(axis=1))[0] # Get the row of the P location
            self.current_matrix[row, 2] -= 1 # Update the number of blocks that the P location has (take 1 block) 
            reward = self.get_reward(self.current_state)

        elif action == 'D':
            row = np.where((self.current_matrix[:,0:2] == self.current_state[0:2]).all(axis=1))[0] # Get the row of the P location
            self.current_matrix[row, 2] += 1 # Update the number of blocks that the P location has (add 1 block) 
            reward = self.get_reward(self.current_state)
        return reward

    def check_walls(self):
        actions = list(self.actions)
        if self.current_state[0] == 0: 
            actions.remove('N')
            if self.current_state[1] == 0: 
                actions.remove('W')
            elif self.current_state[1] == self.width - 1: 
                actions.remove('E')

        if self.current_state[0] == self.height - 1:
            actions.remove('S')
            if self.current_state[1] == 0: 
                actions.remove('W')
            elif self.current_state[1] == self.width - 1: 
                actions.remove('E')

        if self.current_state[1] == 0 and 'W' in actions: 
            actions.remove('W')
            if self.current_state[0] == 0: 
                actions.remove('N')
            elif self.current_state[0] == self.height - 1: 
                actions.remove('S')

        if self.current_state[1] == self.width - 1 and 'E' in actions:
            actions.remove('E')
            if self.current_state[0] == 0: 
                actions.remove('N')
            elif self.current_state[0] == self.height - 1:
                actions.remove('S')
        return actions

    def get_applicable_actions(self):
        applicable_actions = self.check_walls()
        if self.current_state[0:2] in self.current_matrix[:, 0:2]:
            row = np.where((self.current_matrix[:,0:2] == self.current_state[0:2]).all(axis=1))[0]
            if row in [0, 1]:
                if self.current_state[2] == False and self.current_matrix[row, 2] != 0:
                    return 'P'
                else:
                    applicable_actions = [i for i in applicable_actions if i not in ('P', 'D')]
                    return applicable_actions
            else:
                if self.current_state[2] == True and self.current_matrix[row, 2] != 4:
                    return 'D'
                else:
                    applicable_actions = [i for i in applicable_actions if i not in ('P', 'D')]
                    return applicable_actions
        else:
            applicable_actions = [i for i in applicable_actions if i not in ('P', 'D')]
            return applicable_actions
    
    def check_terminal_state(self):
        if (self.current_matrix == self.terminal_matrix).all():
            self.terminal_states_reached += 1
            self.current_state = list(self.initial_state)
            return f'{self.terminal_states_reached} Terminal state(s) reached. Reset current state to initial state.'

cu = PDWorld()
cu.current_state[0:3] = 2, 2, True
print(cu.current_state)
print((cu.current_matrix == cu.current_matrix).all())


import numpy as np
import operator
import time
import random

class PDWorld:
    terminal_states_reached = 0
    def __init__(self):
        #Initialize PDWorld
        self.height = 5
        self.width = 5
        self.grid = np.zeros((self.height, self.width)) - 1

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
        print(np.concatenate((self.grid, grid), axis=1).astype(int), 'Current state: ', self.current_state)
        print(self.current_matrix)

    def get_reward(self, state):
        return self.grid[state[0], state[1]]
    
    def take_action(self, action):
        
        if action == 'N':
            self.current_state[0:2] = [self.current_state[0] - 1, self.current_state[1]]
            reward = -1

        elif action == 'S':
            self.current_state[0:2] = [self.current_state[0] + 1, self.current_state[1]]
            reward = -1

        elif action == 'W':
            self.current_state[0:2] = [self.current_state[0], self.current_state[1] - 1]
            reward = -1
   
        elif action == 'E':
            self.current_state[0:2] = [self.current_state[0], self.current_state[1] + 1]
            reward = -1
        
        elif action == 'P':
            row = np.where((self.current_matrix[:,0:2]== self.current_state[0:2]).all(axis=1))[0] # Get the row of the P location
            self.current_matrix[row, 2] -= 1 # Update the number of blocks that the P location has (take 1 block) 
            self.current_state[2] = True
            reward = 13

        elif action == 'D':
            row = np.where((self.current_matrix[:,0:2] == self.current_state[0:2]).all(axis=1))[0] # Get the row of the P location
            self.current_matrix[row, 2] += 1 # Update the number of blocks that the P location has (add 1 block) 
            self.current_state[2] = False
            reward = 13

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
        if self.current_state[0:2] in self.current_matrix[:, 0:2].tolist():
            row = np.where((self.current_matrix[:, 0:2] == self.current_state[0:2]).all(axis=1))[0]
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
            print(f'{self.terminal_states_reached} Terminal state(s) reached. Reset world to initial state...............')
            self.terminal_states_reached += 1
            self.__init__()
        return 1
            
class Agent():
    def __init__(self, world, alpha = 0.3, gamma = 0.5, epsilon = 0):
        self.world = world

        self.q_table_block = dict()
        for x in range(25): # Initialize q-table with values 0.
            for y in range(6):
                self.q_table_block[x,y] = {'N': 0, 'S': 0, 'W': 0, 'E': 0,'P': 0,'D':0}

        self.q_table_no_block = dict()
        for x in range(25): # Initialize q-table with values 0.
            for y in range(6):
                self.q_table_no_block[x,y] = {'N': 0, 'S': 0, 'W': 0, 'E': 0,'P': 0,'D':0}

        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
    
    def PRANDOM(self, applicable_actions):
        if len(self.world.get_applicable_actions()) == 1:
            action = self.world.get_applicable_actions()
            print('Chosen action:', action)
        else:
            actions = self.world.get_applicable_actions()
            action = actions[random.randint(0,len(actions)-1)]

        return action


    def PGREEDY(self, applicable_actions):
        if len(self.world.get_applicable_actions()) == 1:
            action = self.world.get_applicable_actions()
            print('Chosen action:', action)
        else:
            self.x, self.y = self.world.current_state[0], self.world.current_state[1]
            action = self.world.get_applicable_actions().copy()

            if self.world.current_state[2]: #block
                invalid_actions = list(set(self.q_table_block[self.x, self.y].keys()) - set(action))
                copy_q_table_block = self.q_table_block[self.x, self.y].copy()

                print(copy_q_table_block)
                if invalid_actions :
                    [copy_q_table_block.pop(key) for key in invalid_actions]

                current_state_qvalues = copy_q_table_block
                highestQvalue = max(current_state_qvalues.values())
                action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])
                print('Choose action:', action)

            else:
                invalid_actions = list(set(self.q_table_no_block[self.x, self.y].keys()) - set(action))
                copy_q_table_no_block = self.q_table_no_block[self.x, self.y].copy()

                print(copy_q_table_no_block)
                if invalid_actions :
                    [copy_q_table_no_block.pop(key) for key in invalid_actions]

                current_state_qvalues = copy_q_table_no_block
                highestQvalue = max(current_state_qvalues.values())
                action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])
                print('Choose action:', action)
        return action
    def Q_learning(self, current_state, reward, next_state, action):
        if current_state[2]: #block
            print("CURRENT_STATE 0: ", self.q_table_block[current_state[0], current_state[1]])
            current_qvalue = self.q_table_block[current_state[0], current_state[1]][action]

            next_state_qvalues = self.q_table_block[next_state[0],next_state[1]]
            highest_q_value = max(next_state_qvalues.values())
            current_qvalue = (1 - self.alpha) * current_qvalue + self.alpha * (reward + self.gamma * highest_q_value)

        else:
            print("CURRENT_STATE 0: ",self.q_table_no_block[current_state[0], current_state[1]])
            current_qvalue = self.q_table_no_block[current_state[0], current_state[1]][action]

            next_state_qvalues = self.q_table_no_block[next_state[0],next_state[1]]
            highest_q_value = max(next_state_qvalues.values())

            current_qvalue = (1 - self.alpha) * current_qvalue + self.alpha * (reward + self.gamma * highest_q_value)


def play(world, agent, policy, max_steps):
    total_reward = 0
    step = 0
    while step < max_steps:
        world.print_current_state()
        x, y = world.current_state[0], world.current_state[1]
        # current_state = [x,y]
        if policy == 1:
            action = agent.PRANDOM(world.get_applicable_actions())
        elif policy == 2:
            action = agent.PGREEDY(world.get_applicable_actions())
        elif policy == 3:
            action = agent.PGREEDY(world.get_applicable_actions())
        reward = world.take_action(action)

        next_state = [x, y]
        agent.Q_learning(world.current_state, reward, next_state, action)

        total_reward += reward
        step += 1
        print(f'^^^^^Step {step} out of {max_steps}.^^^^^')
        world.check_terminal_state()
        # time.sleep(0.1)
    print('Number of terminal states the agent reached:', world.terminal_states_reached)
    print('Total reward:', total_reward)
    return total_reward

cu = PDWorld()
to = Agent(cu)
play(cu, to, 2, 6000)

# cu.current_state[0:3] = 2, 2, True
# print(cu.get_applicable_actions())
# print(to.PGREEDY(cu.get_applicable_actions()))



# cu.current_state[0:3] = 2, 2, True
# print(to.PGREEDY(cu.get_applicable_actions()))
# print(len(cu.get_applicable_actions()))


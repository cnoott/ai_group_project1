import numpy as np
import random
import time


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
    def __init__(self, world, alpha, gamma): #world is a PDWorld object
        self.world = world
        self.Q = dict()
        
        self.P = ((2,4),(3,1))
        self.D = ((3,1),(0,0),(0,4),(2,2),(4,4))

        for x in range(50): #50 because 25 coordinates * 2 
            for y in range(6):
                self.Q[(x,y)]= {'NORTH':0,'SOUTH':0,'EAST':0,'WEST':0,'P':0,'D':0}

        self.alpha = alpha
        self.gamma = gamma
    
    def choose_adj_pd(self, world):
        ''' chooses the nearest P or D depending if it has a block or not '''
        if not world.hasBlock: #not holding block
            #North
            new_location = world.current_state
            new_location[0] = world.current_state[0] -1
            if new_location in self.P: #assuming current_state returns tuple
                return 'NORTH'

            #South
            new_location = world.current_state
            new_location[0] = world.current_state[0] +1
            if new_location in self.P:
                return 'SOUTH'

            #East
            new_location = world.current_state
            new_location[1] = world.current_state[1] +1
            if new_location in self.P:
                return 'EAST'

            #West 
            new_location = world.current_state
            new_location[1] = world.current_state[1] -1
            if new_location in self.P:
                return 'WEST'

        elif world.hasBlock:
            #North
            new_location = world.current_state
            new_location[0] = world.current_state[0] -1
            if new_location in self.D: #assuming current_state returns tuple
                return 'NORTH'

            #South
            new_location = world.current_state
            new_location[0] = world.current_state[0] +1
            if new_location in self.D:
                return 'SOUTH'

            #East
            new_location = world.current_state
            new_location[1] = world.current_state[1] +1
            if new_location in self.D:
                return 'EAST'

            #West 
            new_location = world.current_state
            new_location[1] = world.current_state[1] -1
            if new_location in self.D:
                return 'WEST'

        else:
            return '' #aka false

    def check_bounds(self, current_state, direction): #checks if direction is out of bounds (Kien might have done this)
        pass
    
    def get_max_q(self, world): 
        avaliable_directions = {} #ommits directions that are not possible to pass throug
        if not world.hasBlock: #first 25 rows are for not block
            for direction in Q[world.current_state]: 
                if check_direction(world.current_state, direction):
                    avaliable_directions[direction] = Q[world.current_state][direction]
        else:
            for direction in Q[world.current_state+25]: #if has block
                if check_direction(world.current_state, direction):
                    avaliable_directions[direction] = Q[world.current_state+25][direction]
         
        return max(avaliable_directions, key=avaliable_directions.get) #returns max value of dict


            
    
    #choosing an action
    def prandom(self,world):
        ''' Chooses action either by picking adjacent P/D or by random. Retruns string'''
        direction = choose_adj_pd(world)
        if direction: #if no adj pd, returns blank string aka FALSE
            return direction

        else: #need to stop agent from going out of bounds
            directions = ('NORTH','SOUTH','EAST','WEST') 
            return directions[random.randint(0,3)]



    def pexploit(self,world):
        ''' Chooses adjacent P/D. otherwise chooses highest q value'''
        direction = choose_adj_pd(world)
        if direction:
            return direction
        else:
            if random.random() < .8: #choose max q value
                return get_max_q(world)
            else: #choose random
                directions = ('NORTH','SOUTH','EAST','WEST')
                return directions[random.randint(0,3)]


    def pgreedy(self,world):
        direction = choose_adj_pd(world)
        if direction:
            return direction
        else:
            return get_max_q(world)

    def learn(self,old_state, reward, new_state,action):
        q_values = self.Q[new_state]
        max_q_value = max(q_values.values())
        current_q_value = self.Q[old_state][action]

        self.Q[old_state][action] = (1-self.alpha) * current_q_value + self.alpha * (reward + self.gamma * max_q_value)

def play(world, agent, policy, max_steps):
    total_reward = 0
    step = 0
    while step < max_steps:
        world.print_current_state()
        x, y = world.current_state[0], world.current_state[1]
        # current_state = [x,y]
        if policy == 1:
            action = agent.prandom(world.get_applicable_actions())
        elif policy == 2:
            action = agent.pexploit(world.get_applicable_actions())
        elif policy == 3:
            action = agent.pgreedy(world.get_applicable_actions())

        reward = world.take_action(action)
        # next_state = [x, y]
        # agent.Q_learning(current_state, reward, next_state, action) # Comment this out for PRANDOM
        total_reward += reward
        step += 1
        print(f'^^^^^Step {step} out of {max_steps}.^^^^^')
        world.check_terminal_state()
        # time.sleep(0.1)
    print('Number of terminal states the agent reached:', world.terminal_states_reached)
    print('Total reward:', total_reward)
    return total_reward


cu = PDWorld()
to = Agent(cu, 0.3,0.5)
play(cu, to, 1, 6000)


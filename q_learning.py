import numpy as np
import random

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
        self.Q = dict()
        for x in range(world.height+25): #+25 because of q table rows when carrying block
            for y in range(world.width):
                self.[(x,y)]= {'NORTH':0,'SOUTH':0,'EAST':0,'WEST':0,'P':0,'D':0}

        self.alpha = alpha
        self.gamma = gamma
    
    def choose_adj_pd(self, world):
        ''' chooses the nearest P or D depending if it has a block or not '''
        if not world.hasBlock: #not holding block
            #North
            new_location = world.current_location
            new_location[0] = world.current_location[0] -1
            if new_location in self.P: #assuming current_location returns tuple
                return 'NORTH'

            #South
            new_location = world.current_location
            new_location[0] = world.current_location[0] +1
            if new_location in self.P:
                return 'SOUTH'

            #East
            new_location = world.current_location
            new_location[1] = world.current_location[1] +1
            if new_location in self.P:
                return 'EAST'

            #West 
            new_location = world.current_location
            new_location[1] = world.current_location[1] -1
            if new_location in self.P:
                return 'WEST'

        elif world.hasBlock:
            #North
            new_location = world.current_location
            new_location[0] = world.current_location[0] -1
            if new_location in self.D: #assuming current_location returns tuple
                return 'NORTH'

            #South
            new_location = world.current_location
            new_location[0] = world.current_location[0] +1
            if new_location in self.D:
                return 'SOUTH'

            #East
            new_location = world.current_location
            new_location[1] = world.current_location[1] +1
            if new_location in self.D:
                return 'EAST'

            #West 
            new_location = world.current_location
            new_location[1] = world.current_location[1] -1
            if new_location in self.D:
                return 'WEST'

        else:
            return '' #aka false

    def check_bounds(self, current_location, direction): #checks if direction is out of bounds (Kien might have done this)
        pass
    
    def get_max_q(self, world): 
        avaliable_directions = {} #ommits directions that are not possible to pass throug
        if not world.hasBlock: #first 25 rows are for not block
            for direction in Q[world.current_location]: 
                if check_direction(world.current_location, direction):
                    avaliable_directions[direction] = Q[world.current_location][direction]
        else:
            for direction in Q[world.current_location+25]: #if has block
                if check_direction(world.current_location, direction):
                    avaliable_directions[direction] = Q[world.current_location+25][direction]
         
        return max(avaliable_directions, key=avaliable_directions.get) #returns max value of dict


            
    
    #choosing an action
    def prandom(self):
        ''' Chooses action either by picking adjacent P/D or by random. Retruns string'''
        direction = choose_adj_pd(world)
        if direction: #if no adj pd, returns blank string aka FALSE
            return direction

        else: #need to stop agent from going out of bounds
            directions = ('NORTH','SOUTH','EAST','WEST') 
            return directions[random.randint(0,3)]



    def pexploit(self):
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


    def pgreedy(self):
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




import numpy as np
import operator
import time
import random
import matplotlib.pyplot as plt

class PDWorld:
    terminal_states_reached = 0

    def __init__(self):
        # Initialize PDWorld
        self.height = 5
        self.width = 5
        self.grid = np.zeros((self.height, self.width)) - 1

        # Initial state is a tuple since it never changes.
        self.initial_state = (4, 0, False) # The boolean False indicates that the agent does not carry a block and vice versa.
        self.current_state = list(self.initial_state) 

        # Use matrices to store information of P/D locations. Third column is number of blocks in that location. First two rows are for Pickup locations, the other rows are for Dropoff locations.
        self.initial_matrix = np.array([[2, 4, 8], [3, 1, 8], [0, 0, 0], [0, 4, 0], [2, 2, 0], [4, 4, 0]])
        self.current_matrix = self.initial_matrix
        self.terminal_matrix = np.array([[2, 4, 0], [3, 1, 0], [0, 0, 4], [0, 4, 4], [2, 2, 4], [4, 4, 4]])

        # Reward matrix (used only for visualization)
        for i in range(np.shape(self.initial_matrix)[0]):
            self.grid[self.initial_matrix[i][0], self.initial_matrix[i][1]] = 13

        # Set all actions
        self.actions = ('N', 'S', 'W', 'E', 'P', 'D')

    # Show current state
    def print_current_state(self):  # for debugging
        grid = np.zeros((self.height, self.width))
        grid[self.current_state[0], self.current_state[1]] = 1
        print(np.concatenate((self.grid, grid), axis=1).astype(int), ': Current state: ', self.current_state, sep='')
        print(self.current_matrix, ': Current matrix', sep='')

    # Move the agent to the next location according to the chosen action and return the reward.
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
            row = np.where((self.current_matrix[:, 0:2] == self.current_state[0:2]).all(axis=1))[0].tolist() # Get the row of the P location in the matrix
            self.current_matrix[row[0], 2] -= 1 # Update the number of blocks (third column of the matrix) that the P location has (remove 1 block)
            self.current_state[2] = True # The agent is now carrying a block.
            reward = 13

        elif action == 'D':
            row = np.where((self.current_matrix[:, 0:2] == self.current_state[0:2]).all(axis=1))[0].tolist()  # Get the row of the D location in the matrix
            self.current_matrix[row[0], 2] += 1 # Update the number of blocks (third column of the matrix) that the P location has (add 1 block)
            self.current_state[2] = False # The agent is not carrying a block.
            reward = 13

        return reward

    def check_walls(self): # This function will remove invalid actions when the agent is at the edge of the PDWorld map.
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

    def get_applicable_actions(self): # Return applicable actions depending on whether the agent is/is not carrying a block and if the P/D location is empty/full.
        applicable_actions = self.check_walls().copy() # Get applicable actions after they are wall checked.
        applicable_actions_noPD = [i for i in applicable_actions if i not in ('P', 'D')]
        if self.current_state[0:2] in self.current_matrix[:, 0:2].tolist():
            row = np.where((self.current_matrix[:, 0:2] == self.current_state[0:2]).all(axis=1))[0].tolist()
            if row[0] in [0, 1]:
                if self.current_state[2] == False and int(self.current_matrix[row[0], 2]) != 0:
                    return 'P'
                else:
                    return applicable_actions_noPD
            else:
                if self.current_state[2] == True and int(self.current_matrix[row[0], 2]) != 4:
                    return 'D'
                else:
                    return applicable_actions_noPD
        else:
            return applicable_actions_noPD

    def check_terminal_state(self): # Compare current_matrix to terminal_matrix to check terminal state, then if terminal state reaches, return to initial state.
        if (self.current_matrix == self.terminal_matrix).all():
            self.terminal_states_reached += 1
            print(f'{self.terminal_states_reached} Terminal state(s) reached. Reset world to initial state...............')
            self.__init__()
            return True
        else:
            return False
            
class Agent():
    def __init__(self, world, alpha=0.3, gamma=0.5):
        self.world = world
        self.alpha = alpha
        self.gamma = gamma

        self.q_table_block = dict()
        for x in range(25):  # Initialize agent with block q-table with values 0.
            for y in range(6):
                self.q_table_block[x, y] = {'N': 0, 'S': 0, 'W': 0, 'E': 0, 'P': 0, 'D': 0}

        self.q_table_no_block = dict()
        for x in range(25):  # Initialize agent without block q-table with values 0.
            for y in range(6):
                self.q_table_no_block[x, y] = {'N': 0, 'S': 0, 'W': 0, 'E': 0, 'P': 0, 'D': 0}

    def PRANDOM(self, applicable_actions):
        if len(self.world.get_applicable_actions()) == 1: # Choose action P/D if applicable
            action = self.world.get_applicable_actions()
            print('Choose action:', action)
        else:
            actions = self.world.get_applicable_actions() # Otherwise, choose available NSWE action randomly
            action = actions[random.randint(0, len(actions)-1)]
            print('Choose action:', action)
        return action

    def PGREEDY(self, applicable_actions):
        print('Available actions:', self.world.get_applicable_actions()) 
        if len(self.world.get_applicable_actions()) == 1: # Choose action P/D if applicable
            action = self.world.get_applicable_actions()
            print('Choose action:', action)
        else: # Otherwise, choose action with highest q-value
            self.x, self.y = self.world.current_state[0], self.world.current_state[1]
            action = self.world.get_applicable_actions().copy()
            if self.world.current_state[2]:  # Agent with block
                current_state_qvalues = self.q_table_block[self.x, self.y].copy() # Look up the q-table (with block) to get the current state q values
                invalid_actions = list(set(current_state_qvalues.keys()) - set(action)) # Get unused q-values
                if invalid_actions:
                    [current_state_qvalues.pop(key) for key in invalid_actions] # Remove unused q-values
                highestQvalue = max(current_state_qvalues.values())
                action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])
                print('Choose action:', action)

            else: # without block
                current_state_qvalues = self.q_table_no_block[self.x, self.y].copy() # Look up the q-table (without block) to get the current state q values
                invalid_actions = list(set(current_state_qvalues.keys()) - set(action)) # Get unused q-values
                if invalid_actions:
                    [current_state_qvalues.pop(key) for key in invalid_actions] # Remove unused q-values
                highestQvalue = max(current_state_qvalues.values())
                action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])
                print('Choose action:', action)
        return action

    def PEXPLOIT(self, applicable_actions):
        print('Available actions:', self.world.get_applicable_actions())
        #choose P/D action if applicable
        if len(self.world.get_applicable_actions()) == 1:
            action = self.world.get_applicable_actions()
            print('Choose action:',action)
        else:
            if random.random() < .8: #80% chance to choose max q value
                self.x, self.y = self.world.current_state[0], self.world.current_state[1]
                action = self.world.get_applicable_actions().copy()

                if self.world.current_state[2]: # has block
                    current_state_qvalues = self.q_table_block[self.x, self.y].copy()
                    invalid_actions = list(set(current_state_qvalues.keys()) - set(action))

                    if invalid_actions:
                        [current_state_qvalues.pop(key) for key in invalid_actions] #remove unused q values
                    highestQvalue = max(current_state_qvalues.values())
                    action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])
                    print('Choose action:', action)

                else: # no block
                    current_state_qvalues = self.q_table_no_block[self.x, self.y].copy() # Look up the q-table (without block) to get the current state q values
                    invalid_actions = list(set(current_state_qvalues.keys()) - set(action)) # Get unused q-values
                    if invalid_actions:
                        [current_state_qvalues.pop(key) for key in invalid_actions] # Remove unused q-values
                    highestQvalue = max(current_state_qvalues.values())
                    action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])
                    print('Choose action:', action)

            else: #20% chance to choose random
                actions = self.world.get_applicable_actions()
                action = actions[random.randint(0, len(actions)-1)]
                print('Chosen action:', action)

        return action

    def Q_learning(self, current_state, reward, next_state, action):
        if current_state[2]:  # block
            print("Q VALUES WITH BLOCK:", self.q_table_block[current_state[0], current_state[1]], "at", current_state, ":", action)
            next_state_qvalues = self.q_table_block[next_state[0], next_state[1]].copy()
            # Check if a D block is full
            row = np.where((self.world.current_matrix[:, 0:2] == next_state[0:2]).all(axis=1))[0].tolist()
            if row:  # Get the row of the next state if it's a D location
                if self.world.current_matrix[row[0], 2] == 4:
                    del next_state_qvalues['D'], next_state_qvalues['P']
                    highest_q_value = max(next_state_qvalues.values())
                else:
                    highest_q_value = max(next_state_qvalues.values())
            else:
                highest_q_value = max(next_state_qvalues.values())
            print('REWARD:', reward)
            current_q_value = self.q_table_block[current_state[0], current_state[1]][action]
            self.q_table_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * highest_q_value) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_block[current_state[0], current_state[1]], "at", current_state, ":", action)
        else:
            print("Q VALUES WITHOUT BLOCK: ", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state, ":", action)
            next_state_qvalues = self.q_table_no_block[next_state[0], next_state[1]].copy()
            # Check if a P block is empty
            row = np.where((self.world.current_matrix[:, 0:2] == next_state[0:2]).all(axis=1))[0].tolist()
            if row:  # Get the row of the next state if it's a P location
                if self.world.current_matrix[row[0], 2] == 0:
                    del next_state_qvalues['D'], next_state_qvalues['P']
                    highest_q_value = max(next_state_qvalues.values())
                else:
                    highest_q_value = max(next_state_qvalues.values())
            else:
                highest_q_value = max(next_state_qvalues.values())
            print('REWARD:', reward)
            current_q_value = self.q_table_no_block[current_state[0], current_state[1]][action]
            self.q_table_no_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * highest_q_value) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state, ":", action)
            
    def SARSA(self, current_state, reward, next_state, action):
        if current_state[2]:  # block
            print("Q VALUES WITH BLOCK:", self.q_table_block[current_state[0], current_state[1]], "at", current_state, ":", action)
            next_state_action = self.PEXPLOIT(self.world.get_applicable_actions())
            next_state_qvalue = self.q_table_block[next_state[0], next_state[1]][next_state_action]
            print('REWARD:', reward)
            current_q_value = self.q_table_block[current_state[0], current_state[1]][action]
            self.q_table_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * next_state_qvalue) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_block[current_state[0], current_state[1]], "at", current_state, ":", action)
        else:
            print("Q VALUES WITHOUT BLOCK: ", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state, ":", action)
            next_state_action = self.PEXPLOIT(self.world.get_applicable_actions())
            next_state_qvalue = self.q_table_no_block[next_state[0], next_state[1]][next_state_action]
            print('REWARD:', reward)
            current_q_value = self.q_table_no_block[current_state[0], current_state[1]][action]
            self.q_table_no_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * next_state_qvalue) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state, ":", action)

    def print_QTable(self):
        print('\nQ TABLE WITHOUT BLOCK:')
        for x in range(self.world.height):
            for y in range(self.world.width):
                print(f'({x},{y}): ', end='')
                for k, v in self.q_table_no_block[x, y].items():
                    v = round(v, 4)
                    print(f'{k}: {v:.4f}','\t', end='', sep='')
                print()
        print('\nQ TABLE WITH BLOCK:')
        for x in range(self.world.height):
            for y in range(self.world.width):
                print(f'({x},{y}): ', end='')
                for k, v in self.q_table_block[x, y].items():
                    v = round(v, 4)
                    print(f'{k}: {v:.4f}','\t', end='', sep='')
                print()

def play(world, agent, policy, max_steps, SARSA=False):
    reward_per_episode = 0
    total_reward = 0
    step = 0
    reward_log = []
    terminal_steps = []
    terminal_y = []
    while step < 500:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        current_state = world.current_state.copy()
        action = agent.PRANDOM(world.get_applicable_actions())
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('Next state:', next_state)
        agent.Q_learning(current_state, reward, next_state, action)

        reward_per_episode += reward
        total_reward += reward
        if world.check_terminal_state():
            terminal_steps.append(step-1)
            terminal_y.append(total_reward)
            reward_per_episode = 0
        reward_log.append(total_reward)
    while step < max_steps:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        current_state = world.current_state.copy()
        if policy == 1:
            action = agent.PRANDOM(world.get_applicable_actions())
        elif policy == 2:
            action = agent.PEXPLOIT(world.get_applicable_actions())
        elif policy == 3:
            action = agent.PGREEDY(world.get_applicable_actions())
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('Next state:', next_state)
        agent.SARSA(current_state, reward, next_state, action) if SARSA else agent.Q_learning(current_state, reward, next_state, action)

        reward_per_episode += reward
        total_reward += reward
        if world.check_terminal_state():
            terminal_steps.append(step-1)
            terminal_y.append(total_reward)
            reward_per_episode = 0
        reward_log.append(total_reward)
    print('Number of terminal states the agent reached:', world.terminal_states_reached)
    print('Total reward:', total_reward)
    agent.print_QTable()
    return reward_log, terminal_steps, terminal_y

environment = PDWorld()
agent = Agent(environment)
log, steps, y = play(environment, agent, 3, 6000, SARSA=False)

plt.plot(log)
plt.scatter(steps,y, marker=',', color='r')
plt.show()
import numpy as np
import operator
import time
import random
import matplotlib.pyplot as plt
from  matplotlib.tri import Triangulation

class PDWorld:
    terminal_states_reached = 0
    initial_matrix = np.array([[2, 4, 8], [3, 1, 8], [0, 0, 0], [0, 4, 0], [2, 2, 0], [4, 4, 0]])
    terminal_matrix = np.array([[2, 4, 0], [3, 1, 0], [0, 0, 4], [0, 4, 4], [2, 2, 4], [4, 4, 4]])
    def __init__(self):
        # Initialize PDWorld
        self.height = 5
        self.width = 5

        # Self.grid matrix is for displaying the reward matrix
        self.grid = np.empty((self.height, self.width), dtype=object)
        self.grid[:] = '-1'
        for i in range(2,6):
            self.grid[self.initial_matrix[i][0], self.initial_matrix[i][1]] = ' D'
        self.grid[2,4] = self.grid[3,1] = ' P'

        # Initial state is a tuple since it never changes.
        self.initial_state = (4, 0, False) # The boolean False indicates that the agent does not carry a block and vice versa.
        self.current_state = list(self.initial_state) 

        # Use matrices to store information of P/D locations. Third column is number of blocks in that location. First two rows are for Pickup locations, the other rows are for Dropoff locations.
        self.initial_matrix = PDWorld.initial_matrix.copy()
        self.current_matrix = self.initial_matrix
        self.terminal_matrix = PDWorld.terminal_matrix.copy()

        # Set all actions
        self.actions = ('N', 'S', 'W', 'E', 'P', 'D')

    # Show current state
    def print_current_state(self):  # for debugging
        grid = np.zeros((self.height, self.width), dtype=int)
        grid[self.current_state[0], self.current_state[1]] = 1
        print(np.concatenate((self.grid, grid), axis=1).astype(object), ': Current state: ', self.current_state, sep='')
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
            row = np.where((self.current_state[0:2] == self.current_matrix[:, 0:2]).all(axis=1))[0].tolist() # Get the row of the P location in the matrix
            self.current_matrix[row[0], 2] -= 1 # Update the number of blocks (third column of the matrix) that the P location has (remove 1 block)
            self.current_state[2] = True # The agent is now carrying a block.
            reward = 13

        elif action == 'D':
            row = np.where((self.current_state[0:2] == self.current_matrix[:, 0:2]).all(axis=1))[0].tolist()  # Get the row of the D location in the matrix
            self.current_matrix[row[0], 2] += 1 # Update the number of blocks (third column of the matrix) that the D location has (add 1 block)
            self.current_state[2] = False # The agent is not carrying a block anymore.
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

    def get_applicable_actions(self): # Return applicable actions depending on whether the agent has a block or not and if the P/D location is empty/full.
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
    def __init__(self, world, alpha, gamma):
        self.world = world
        self.alpha = alpha
        self.gamma = gamma

        self.q_table_block = dict()
        for x in range(5):  # Initialize agent with block q-table with values 0.
            for y in range(5):
                self.q_table_block[x, y] = {'N': 0, 'S': 0, 'W': 0, 'E': 0, 'P': 0, 'D': 0}

        self.q_table_no_block = dict()
        for x in range(5):  # Initialize agent without block q-table with values 0.
            for y in range(5):
                self.q_table_no_block[x, y] = {'N': 0, 'S': 0, 'W': 0, 'E': 0, 'P': 0, 'D': 0}

    def PRANDOM(self, applicable_actions):
        if len(self.world.get_applicable_actions()) == 1: # Choose action P/D if applicable
            action = self.world.get_applicable_actions()
        else:
            actions = self.world.get_applicable_actions() # Otherwise, choose available NSWE action randomly
            action = actions[random.randint(0, len(actions)-1)]
        return action

    def PGREEDY(self, applicable_actions):
        if len(self.world.get_applicable_actions()) == 1: # Choose action P/D if applicable
            action = self.world.get_applicable_actions()
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

            else: # without block
                current_state_qvalues = self.q_table_no_block[self.x, self.y].copy() # Look up the q-table (without block) to get the current state q values
                invalid_actions = list(set(current_state_qvalues.keys()) - set(action)) # Get unused q-values
                if invalid_actions:
                    [current_state_qvalues.pop(key) for key in invalid_actions] # Remove unused q-values
                highestQvalue = max(current_state_qvalues.values())
                action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])

        return action

    def PEXPLOIT(self, applicable_actions):
        # Choose P/D action if applicable
        if len(self.world.get_applicable_actions()) == 1:
            action = self.world.get_applicable_actions()
        else:
            if random.random() < .8: # 80% chance to choose max q value
                self.x, self.y = self.world.current_state[0], self.world.current_state[1]
                action = self.world.get_applicable_actions().copy()

                if self.world.current_state[2]: # has block
                    current_state_qvalues = self.q_table_block[self.x, self.y].copy()
                    invalid_actions = list(set(current_state_qvalues.keys()) - set(action))

                    if invalid_actions:
                        [current_state_qvalues.pop(key) for key in invalid_actions] #remove unused q values
                    highestQvalue = max(current_state_qvalues.values())
                    action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])

                else: # no block
                    current_state_qvalues = self.q_table_no_block[self.x, self.y].copy() # Look up the q-table (without block) to get the current state q values
                    invalid_actions = list(set(current_state_qvalues.keys()) - set(action)) # Get unused q-values
                    if invalid_actions:
                        [current_state_qvalues.pop(key) for key in invalid_actions] # Remove unused q-values
                    highestQvalue = max(current_state_qvalues.values())
                    action = np.random.choice([k for k, v in current_state_qvalues.items() if v == highestQvalue])

            else: # 20% chance to choose random
                actions = self.world.get_applicable_actions()
                action = actions[random.randint(0, len(actions)-1)]

        return action

    def Q_learning(self, current_state, reward, next_state, action):
        if current_state[2]:  # block
            print("Q VALUES WITH BLOCK:", self.q_table_block[current_state[0], current_state[1]], "at", current_state)
            next_state_qvalues = self.q_table_block[next_state[0], next_state[1]].copy()
            # Check if a D block is full
            row = np.where((next_state[0:2] == self.world.current_matrix[:, 0:2]).all(axis=1))[0].tolist()
            if row:  # Get the row of the next state if it's a D location
                if self.world.current_matrix[row[0], 2] == 4:
                    del next_state_qvalues['D']
                    del next_state_qvalues['P']
                    highest_q_value = max(next_state_qvalues.values())
                else:
                    highest_q_value = max(next_state_qvalues.values())
            else:
                highest_q_value = max(next_state_qvalues.values())
            print('REWARD:', reward)
            current_q_value = self.q_table_block[current_state[0], current_state[1]][action]
            self.q_table_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * highest_q_value) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_block[current_state[0], current_state[1]], "at", current_state)
        else:
            print("Q VALUES WITHOUT BLOCK: ", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state)
            next_state_qvalues = self.q_table_no_block[next_state[0], next_state[1]].copy()
            # Check if a P block is empty
            row = np.where((next_state[0:2] == self.world.current_matrix[:, 0:2]).all(axis=1))[0].tolist()
            if row:  # Get the row of the next state if it's a P location
                if self.world.current_matrix[row[0], 2] == 0:
                    del next_state_qvalues['D']
                    del next_state_qvalues['P']
                    highest_q_value = max(next_state_qvalues.values())
                else:
                    highest_q_value = max(next_state_qvalues.values())
            else:
                highest_q_value = max(next_state_qvalues.values())
            print('REWARD:', reward)
            current_q_value = self.q_table_no_block[current_state[0], current_state[1]][action]
            self.q_table_no_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * highest_q_value) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state)
            
    def SARSA(self, current_state, reward, next_state, action):
        if current_state[2]:  # block
            print("Q VALUES WITH BLOCK:", self.q_table_block[current_state[0], current_state[1]], "at", current_state)
            next_state_action = self.PEXPLOIT(self.world.get_applicable_actions())
            next_state_qvalue = self.q_table_block[next_state[0], next_state[1]][next_state_action]
            print('REWARD:', reward)
            current_q_value = self.q_table_block[current_state[0], current_state[1]][action]
            self.q_table_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * next_state_qvalue) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_block[current_state[0], current_state[1]], "at", current_state)
        else:
            print("Q VALUES WITHOUT BLOCK: ", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state)
            next_state_action = self.PEXPLOIT(self.world.get_applicable_actions())
            next_state_qvalue = self.q_table_no_block[next_state[0], next_state[1]][next_state_action]
            print('REWARD:', reward)
            current_q_value = self.q_table_no_block[current_state[0], current_state[1]][action]
            self.q_table_no_block[current_state[0], current_state[1]][action] = (
                1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * next_state_qvalue) # Update Q values
            print("UPDATED Q VALUES:", self.q_table_no_block[current_state[0], current_state[1]], "at", current_state)

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

    def return_Q_values(self): # for heatmap
        ''' Returns tuple of q_table with block and wihout '''

        # with block
        N_block = np.arange(25,dtype=float).reshape(5,5)
        E_block = np.arange(25,dtype=float).reshape(5,5)
        S_block = np.arange(25,dtype=float).reshape(5,5)
        W_block = np.arange(25,dtype=float).reshape(5,5)

        # no block
        N = np.arange(25,dtype=float).reshape(5,5)
        E = np.arange(25,dtype=float).reshape(5,5)
        S = np.arange(25,dtype=float).reshape(5,5)
        W = np.arange(25,dtype=float).reshape(5,5)

        #get values
        for i in range(5):
            for j in range(5):
                N_block[i][j] = self.q_table_block[i,j]['N']
                E_block[i][j] = self.q_table_block[i,j]['E']
                S_block[i][j] = self.q_table_block[i,j]['S']
                W_block[i][j] = self.q_table_block[i,j]['W']
                N[i][j] = self.q_table_no_block[i,j]['N']
                E[i][j] = self.q_table_no_block[i,j]['E']
                S[i][j] = self.q_table_no_block[i,j]['S']
                W[i][j] = self.q_table_no_block[i,j]['W']

        return ([N_block,E_block,S_block,W_block], [N,E,S,W])

def play(world, agent, policy, max_steps, SARSA=False):
    reward_per_episode = 0
    reward_per_episode_log = [0]
    total_reward = 0
    step = 0
    reward_log = []
    terminal_steps = [0]
    terminal_y = []
    while step < 500:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        current_state = world.current_state.copy()
        print('Available actions:', world.get_applicable_actions()) 
        action = agent.PRANDOM(world.get_applicable_actions())
        print('Choose action:', action)
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('Next state:', next_state)
        agent.Q_learning(current_state, reward, next_state, action)

        reward_per_episode += reward
        total_reward += reward
        if world.check_terminal_state():
            terminal_steps.append(step-1)
            terminal_y.append(total_reward)
            reward_per_episode_log.append(reward_per_episode)
            reward_per_episode = 0
        reward_log.append(total_reward)
    while step < max_steps:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        current_state = world.current_state.copy()
        print('Available actions:', world.get_applicable_actions())
        if policy == 1:
            action = agent.PRANDOM(world.get_applicable_actions())
            graph_policy = 'PRANDOM'
        elif policy == 2:
            action = agent.PEXPLOIT(world.get_applicable_actions())
            graph_policy = 'PEXPLOIT'
        elif policy == 3:
            action = agent.PGREEDY(world.get_applicable_actions())
            graph_policy = 'PGREEDY'
        print('Choose action:', action)
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('Next state:', next_state)
        agent.SARSA(current_state, reward, next_state, action) if SARSA else agent.Q_learning(current_state, reward, next_state, action)
        reward_per_episode += reward
        total_reward += reward
        if world.check_terminal_state():
            terminal_steps.append(step-1)
            terminal_y.append(total_reward)
            reward_per_episode_log.append(reward_per_episode)
            reward_per_episode = 0
        reward_log.append(total_reward)
    print('Number of terminal states the agent reached:', world.terminal_states_reached)
    print('Total reward:', total_reward)
    agent.print_QTable()

    q_values = agent.return_Q_values()
    if SARSA:
        title = f'{graph_policy} with SARSA=True (alpha={agent.alpha}, gamma={agent.gamma})'
    else:
        title = f'{graph_policy} with SARSA=False (alpha={agent.alpha}, gamma={agent.gamma})'
    return reward_log, terminal_steps, terminal_y, reward_per_episode_log, q_values, title #q_values for heatmap

def exp4(world, agent, policy, max_steps, SARSA=False):
    reward_per_episode = 0
    reward_per_episode_log = [0]
    total_reward = 0
    step = 0
    reward_log = []
    terminal_steps = [0]
    terminal_y = []
    flag = True
    while step < 500:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        current_state = world.current_state.copy()
        print('Available actions:', world.get_applicable_actions())
        action = agent.PRANDOM(world.get_applicable_actions())
        print('Choose action:', action)
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('Next state:', next_state)
        agent.Q_learning(current_state, reward, next_state, action)

        reward_per_episode += reward
        total_reward += reward
        if world.check_terminal_state():
            terminal_steps.append(step-1)
            terminal_y.append(total_reward)
            reward_per_episode_log.append(reward_per_episode)
            reward_per_episode = 0

        if len(terminal_steps) == 4 and flag == True:
            PDWorld.initial_matrix[0] = [2, 0, 8]
            PDWorld.initial_matrix[1] = [0, 2, 8]
            PDWorld.terminal_matrix[0] = [2, 0, 0]
            PDWorld.terminal_matrix[1] = [0, 2, 0]
            world.__init__()
            flag = False

        reward_log.append(total_reward)
    while step < max_steps:
        step += 1
        print(f'----------------------Step {step} out of {max_steps}.----------------------')
        world.print_current_state()
        current_state = world.current_state.copy()
        print('Available actions:', world.get_applicable_actions())
        if policy == 1:
            action = agent.PRANDOM(world.get_applicable_actions())
            graph_policy = 'PRANDOM'
        elif policy == 2:
            action = agent.PEXPLOIT(world.get_applicable_actions())
            graph_policy = 'PEXPLOIT'
        elif policy == 3:
            action = agent.PGREEDY(world.get_applicable_actions())
            graph_policy = 'PGREEDY'
        print('Choose action:', action)
        reward = world.take_action(action)
        next_state = world.current_state.copy()
        print('Next state:', next_state)
        agent.SARSA(current_state, reward, next_state, action) if SARSA else agent.Q_learning(current_state, reward, next_state, action)

        reward_per_episode += reward
        total_reward += reward
        if world.check_terminal_state():
            terminal_steps.append(step-1)
            terminal_y.append(total_reward)
            reward_per_episode_log.append(reward_per_episode)
            reward_per_episode = 0

        if len(terminal_steps) == 4 and flag == True:
            PDWorld.initial_matrix[0] = [2, 0, 8]
            PDWorld.initial_matrix[1] = [0, 2, 8]
            PDWorld.terminal_matrix[0] = [2, 0, 0]
            PDWorld.terminal_matrix[1] = [0, 2, 0]
            world.__init__()
            flag = False

        if len(terminal_steps) == 7:
              break
        reward_log.append(total_reward)
    print('Number of terminal states the agent reached:', world.terminal_states_reached)
    print('Total reward:', total_reward)
    agent.print_QTable()

    q_values = agent.return_Q_values()
    if SARSA:
        title = f'{graph_policy} with SARSA=True (alpha={agent.alpha}, gamma={agent.gamma})'
    else:
        title = f'{graph_policy} with SARSA=False (alpha={agent.alpha}, gamma={agent.gamma})'
    return reward_log, terminal_steps, terminal_y, reward_per_episode_log, q_values, title # q_values for heatmap

environment = PDWorld()
agent = Agent(environment, alpha=0.3, gamma=0.5)
log, terminal_steps, y, reward_per_episode_log, q_values, title = play(environment, agent, 3, 6000, SARSA=True)
# log, terminal_steps, y, reward_per_episode_log,q_values, title = exp4(environment, agent, 2, 6000, SARSA=True) # Experiment 4

# Get values for graphs
steps_between_terminal_states = [0]
for step in range(1, len(terminal_steps)):
    steps = terminal_steps[step] - terminal_steps[step-1]
    steps_between_terminal_states.append(steps)
terminal_states_number = []
for i in range(len(steps_between_terminal_states)):
    i=i
    terminal_states_number.append(i)

# Figure 1
plt.plot(log)
plt.xlabel('Step')
plt.ylabel('Total reward')
plt.title(title)
plt.scatter(terminal_steps[1:], y, marker=',', color='r')

# Figure 2
fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(6,6))
fig.suptitle(title)
fig.text(0.5, 0.04,'Terminal state', ha='center')
ax1.set_ylabel('Steps to reach a terminal state')
ax2.set_ylabel('Reward per episode')
ax1.plot(terminal_states_number, steps_between_terminal_states)
ax2.plot(terminal_states_number, reward_per_episode_log)
plt.locator_params(axis="both", integer=True)
plt.xticks(np.arange(0, len(terminal_states_number), 1))

# Heatmap
q_values_block = q_values[0]
q_values_no_block = q_values[1]

print("q values with block", q_values_block)
print('q values without block', q_values_no_block)

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

#plotting with block
M, N = 5,5
triangul = triangulation_for_triheatmap(M, N)
values = q_values_block
cmaps = ['Blues', 'Greens', 'Purples', 'Reds']  # ['winter', 'spring', 'summer', 'autumn']
norms = [plt.Normalize(-0.5, 1) for _ in range(4)]
fig, ax = plt.subplots()

plt.title(title + ' with block')
imgs = [ax.tripcolor(t, val.ravel(), cmap='RdYlGn',  vmin=-1.2, vmax=1, ec='white')
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

imgs = [ax.tripcolor(t, val.ravel(), cmap='RdYlGn', vmin=-1.1, vmax=0, ec='white')
                for t, val in zip(triangul, values)]

plt.title(title + ' no block')
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

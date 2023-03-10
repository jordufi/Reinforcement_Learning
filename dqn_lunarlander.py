# -*- coding: utf-8 -*-
"""DQN_LunarLander.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j-AlgaqCmBRxeQps2eCrPQVWwRGZ5Z7D
"""

!apt-get install -y xvfb python-opengl > /dev/null 2>&1

!pip install gym pyvirtualdisplay > /dev/null 2>&1

"""##Libraries"""

import gym
import numpy as np
from tensorflow import keras
import matplotlib.pyplot as plt
import time
import random
from IPython import display as ipythondisplay

from pyvirtualdisplay import Display
display = Display(visible=0, size=(400, 300))
display.start()

pip install gym[classic_control]

"""## Hyperparameters"""

pip install gym[box2d]

GAMMA = 0.99
MEMORY_SIZE = 100000#100000
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EXPLORATION_MAX = 0.9
EXPLORATION_MIN = 0.01
EXPLORATION_DECAY = 0.99925
NUMBER_OF_EPISODES =50 #300
MAX_STEPS = 10000#antes 500

GAMMA = 0.999
MEMORY_SIZE = 100000#100000
LEARNING_RATE = 0.001
BATCH_SIZE = 32
EXPLORATION_MAX = 0.9
EXPLORATION_MIN = 0.01
EXPLORATION_DECAY = 0.99925
NUMBER_OF_EPISODES =50 #300
MAX_STEPS = 500#antes 500

#este no aparca, pero se queda flotando
GAMMA = 0.99
MEMORY_SIZE = 1000000
LEARNING_RATE = 0.001
BATCH_SIZE = 64
EXPLORATION_MAX = 1
EXPLORATION_MIN = 0.01
EXPLORATION_DECAY = 0.99975
NUMBER_OF_EPISODES = 150
MAX_STEPS = 500

GAMMA = 0.99
MEMORY_SIZE = 1000000
LEARNING_RATE = 0.001
BATCH_SIZE = 64
EXPLORATION_MAX = 1
EXPLORATION_MIN = 0.03
EXPLORATION_DECAY = 0.99985
NUMBER_OF_EPISODES = 350
MAX_STEPS = 1000

pip show gym

pip show numpy

"""## Class ReplayMemory

Memory of transitions for experience replay.
"""

class ReplayMemory:

    def __init__(self,number_of_observations):
        # Create replay memory
        self.states = np.zeros((MEMORY_SIZE, number_of_observations))
        self.states_next = np.zeros((MEMORY_SIZE, number_of_observations))
        self.actions = np.zeros(MEMORY_SIZE, dtype=np.int32)
        self.rewards = np.zeros(MEMORY_SIZE)
        self.terminal_states = np.zeros(MEMORY_SIZE, dtype=bool)
        self.current_size=0

    def store_transition(self, state, action, reward, state_next, terminal_state):
        # Store a transition (s,a,r,s') in the replay memory
        i = self.current_size
        self.states[i] = state
        self.states_next[i] = state_next
        self.actions[i] = action
        self.rewards[i] = reward
        self.terminal_states[i] = terminal_state
        self.current_size = i + 1

    def sample_memory(self, batch_size):
        # Generate a sample of transitions from the replay memory
        batch = np.random.choice(self.current_size, batch_size)
        states = self.states[batch]
        states_next = self.states_next[batch]
        rewards = self.rewards[batch]
        actions = self.actions[batch]   
        terminal_states = self.terminal_states[batch]  
        return states, actions, rewards, states_next, terminal_states

"""## Class DQN

Reinforcement learning agent with a Deep Q-Network.
"""

class DQN:

    def __init__(self, number_of_observations, number_of_actions):
        # Initialize variables and create neural model
        self.exploration_rate = EXPLORATION_MAX
        self.number_of_actions = number_of_actions
        self.number_of_observations = number_of_observations
        self.scores = []
        self.memory = ReplayMemory(number_of_observations)
        self.model = keras.models.Sequential()
        self.model.add(keras.layers.Dense(64, input_shape=(number_of_observations,), \
                             activation="relu",kernel_initializer="he_normal"))
        #self.model.add(keras.layers.Dense(164, input_shape=(number_of_observations,), \
        #                    activation="relu",kernel_initializer="he_normal"))
        self.model.add(keras.layers.Dense(64, activation="relu",kernel_initializer="he_normal"))
        #self.model.add(keras.layers.Dense(32, activation="relu",kernel_initializer="he_normal"))

        self.model.add(keras.layers.Dense(number_of_actions, activation="linear"))
        self.model.compile(loss="mse", optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE))

    def remember(self, state, action, reward, next_state, terminal_state):
        # Store a tuple (s, a, r, s') for experience replay
        state = np.reshape(state, [1, self.number_of_observations])
        next_state = np.reshape(next_state, [1, self.number_of_observations])
        self.memory.store_transition(state, action, reward, next_state, terminal_state)

    def select(self, state):
        # Generate an action for a given state using epsilon-greedy policy
        if np.random.rand() < self.exploration_rate:
            return random.randrange(self.number_of_actions)
        else:
            state = np.reshape(state, [1, self.number_of_observations])
            q_values = self.model.predict(state, verbose=0)
            return np.argmax(q_values[0])

    def learn(self):
        # Learn the value Q using a sample of examples from the replay memory
        if self.memory.current_size < BATCH_SIZE: return

        states, actions, rewards, next_states, terminal_states = self.memory.sample_memory(BATCH_SIZE)

        q_targets = self.model.predict(states, verbose=0)
        q_next_states = self.model.predict(next_states, verbose=0)

        for i in range(BATCH_SIZE):
             if (terminal_states[i]):
                  q_targets[i][actions[i]] = rewards[i]
             else:
                  q_targets[i][actions[i]] = rewards[i] + GAMMA * np.max(q_next_states[i])    

        self.model.train_on_batch(states, q_targets)

        # Decrease exploration rate
        self.exploration_rate *= EXPLORATION_DECAY
        self.exploration_rate = max(EXPLORATION_MIN, self.exploration_rate)

    def add_score(self, score):
       # Add the obtained score in a list to be presented later
        self.scores.append(score)

    def display_scores_graphically(self):
        # Display the obtained scores graphically
        plt.plot(self.scores)
        plt.xlabel("Episode")
        plt.ylabel("Score")

def create_environment():
    # Create simulated environment
    environment = gym.make(
    "LunarLander-v2",
    continuous= False,#cambiar
    gravity=-10.0,
    enable_wind=False,
    wind_power = 15.0,
    turbulence_power = 1.5,
)
    number_of_observations = environment.observation_space.shape[0]#8
    number_of_actions = 4#environment.action_space.n#
    return environment, number_of_observations, number_of_actions

def create_environment():
    # Create simulated environment
    environment = gym.make(
    "LunarLander-v2"
)
    number_of_observations = environment.observation_space.shape[0]#8
    number_of_actions = environment.action_space.n#4#environment.action_space.n#
    return environment, number_of_observations, number_of_actions

import gym
env = gym.make(
    "LunarLander-v2",
    continuous= False,
    gravity=-10.0,
    enable_wind=False,
    wind_power = 15.0,
    turbulence_power = 1.5,
)

env.observation_space.shape[0]

env.action_space.n

"""## Main program



"""

img_array = []
environment, number_of_observations, number_of_actions = create_environment()
agent = DQN(number_of_observations, number_of_actions)
environment.reset()
prev_screen = environment.render(mode='rgb_array')
img_array.append(prev_screen)
plt.imshow(prev_screen)
episode = 0
goal_reached = False
start_time = time.perf_counter()
while (episode < NUMBER_OF_EPISODES) and not (goal_reached):
    
    episode += 1
    step = 1
    end_episode = False
    state = environment.reset()
    total_reward=0
    while not(end_episode):
        # Select an action for the current state
        action = agent.select(state)

        # Execute the action in the environment
        state_next, reward, terminal_state, info = environment.step(action)
        #print("state_next")
        #print(state_next)
        #print("reward")
        #print(reward)
        #print("terminal_state")
        #print(terminal_state)
        #print("info")
        #print(info)
        #print("e")
        #print(e)
        if episode>= NUMBER_OF_EPISODES-5:
          screen = environment.render(mode='rgb_array')
          img_array.append(screen)

        # Store in memory the transition (s,a,r,s') 
        agent.remember(state, action, reward, state_next, terminal_state)
        #ACABAR PREMATURAMENTE
        #if state[6]==1 and state[7]==1:
          #terminal_state=True          
        total_reward += reward

        # Learn using a batch of experience stored in memory
        agent.learn()
  
        # Detect end of episode and print
        if terminal_state or step >= MAX_STEPS:
            #print("len realidad este reward ha sido de")
            #print(total_reward)
            total_reward=total_reward#-0.05*step
            agent.add_score(total_reward)
            #if step >= MAX_STEPS: goal_reached = True
            print("Episode {0:>3}: ".format(episode), end = '')
            print("score {0:>3} ".format(total_reward), end = '') 
            print("(exploration rate: %.2f, " % agent.exploration_rate, end = '')
            print("transitions: " + str(agent.memory.current_size) + ")")
            end_episode = True 
        else:
            state = state_next
            step += 1

if goal_reached: print("Reached goal sucessfully.")
else: print("Failure to reach the goal.")

print ("Time:", round((time.perf_counter() - start_time)/60), "minutes")

agent.display_scores_graphically()

agent.display_scores_graphically()

ipythondisplay.clear_output(wait=True)
env.close()



from matplotlib import rc
rc('animation', html='jshtml')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots()
frames = [[ax.imshow(img_array[i])] for i in range(len(img_array))]
ani = animation.ArtistAnimation(fig, frames)
ani

ani



GAMMA = 0.99
MEMORY_SIZE = 1000000
LEARNING_RATE = 0.001
BATCH_SIZE = 64
EXPLORATION_MAX = 1
EXPLORATION_MIN = 0.01
EXPLORATION_DECAY = 0.99995
NUMBER_OF_EPISODES = 400
MAX_STEPS = 1000

agent.model.save_weights('lunar_lander.h5')
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from matplotlib import pyplot as plt
import random
from collections import namedtuple
from itertools import count
from PIL import Image
import torch
import torch.optim as optim
import torch.nn.functional as F

from ENVManager_2 import SnakeEnvManager
from EnvManager import CartPoleEnvManager

from NN import DQN
from ReplayMemory import ReplayMemory
from Strategy import EpsilonGreedyStrategy
from Agent import Agent
  

Experience = namedtuple('Experience', ('state', 'action', 'next_state', 'reward'))
                  
        
def plot(values, moving_avg_period):
    plt.figure(2)
    plt.clf()
    plt.title('Training..')
    plt.xlabel('Episode')
    plt.ylabel('Duration')
    plt.plot(values)
    plt.plot(get_moving_average(moving_avg_period, values))
    plt.pause(0.001) 
    
def get_moving_average(period, values):
    values = torch.tensor(values, dtype=torch.float)
    if len(values) >= period:
        moving_avg = values.unfold(dimension=0, size=period, step=1).mean(dim=1).flatten(start_dim=0)
        moving_avg = torch.cat((torch.zeros(period-1), moving_avg))
        return moving_avg.numpy()
    else:
        moving_avg = torch.zeros(len(values))
        return moving_avg.numpy()
  
class QValues():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    @staticmethod
    def get_current(policy_net, states, actions):
        return policy_net(states).gather(dim=1, index=actions.unsqueeze(-1))
        
    @staticmethod
    def get_next(target_net, next_states):
        final_state_locations = next_states.flatten(start_dim=1).max(dim=1)[0].eq(0).type(torch.bool)
        non_final_state_locations = (final_state_locations == False)
        non_final_states = next_states[non_final_state_locations]
        batch_size = next_states.shape[0]
        values = torch.zeros(batch_size).to(QValues.device)
        values[non_final_state_locations] = target_net(non_final_states).max(dim=1)[0].detach()
        return values
  
def extract_tensors(experiences):
    batch = Experience(*zip(*experiences))
    
    t1 = torch.cat(batch.state)
    t2 = torch.cat(batch.action)
    t3 = torch.cat(batch.reward)
    t4 = torch.cat(batch.next_state)
    
    return (t1, t2, t3, t4)
    
       
def main():
    batch_size = 200
    gamma = 0.999
    eps_start = 1
    eps_end = 0.0003
    eps_decay = 0.0001
    target_update = 100
    memory_size = 15000
    lr = 0.001
    num_episodes = 100000

    # check mps or cuda available and assign device
    if torch.cuda.is_available():
        print("Using CUDA")
        device = torch.device("cuda")
    # elif torch.backends.mps.is_available():
    #     print("Using MPS")
    #     device = torch.device("mps")
    else:
        print("Using CPU")
        device = torch.device("cpu")

    em = SnakeEnvManager(device)
    input("Enter to continue...")
    # em = CartPoleEnvManager(device)
    strategy = EpsilonGreedyStrategy(eps_start, eps_end, eps_decay)
    agent = Agent(strategy, em.num_actions_available(), device)
    memory = ReplayMemory(memory_size)
    policy_net = DQN(em.get_screen_height(), em.get_screen_width()).to(device)
    target_net = DQN(em.get_screen_height(), em.get_screen_width()).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    optimizer = optim.Adam(params=policy_net.parameters(), lr=lr)
    
    episode_durations = []

    for episode in count():
        em.reset()
        state = em.get_state()
        episode_rewards = 0
        for timestep in count():
            print(agent.strategy.epsilon)
            print("Epsiode: {}".format(episode))
            action = agent.select_action(state, policy_net)
            reward = em.take_action(action)
            next_state = em.get_state()
            memory.push(Experience(state, action, next_state, reward))
            state = next_state
            
            episode_rewards += reward
            
            # screen = next_state
            # plt.figure()
            # plt.imshow(screen.squeeze(0).permute(1, 2, 0), interpolation='none')
            # plt.show()
            
            if memory.can_provide_sample(batch_size):
                experiences = memory.sample(batch_size)
                states, actions, rewards, next_states = extract_tensors(experiences)
                
                current_q_values = QValues.get_current(policy_net, states, actions)
                next_q_values = QValues.get_next(target_net, next_states)
                target_q_values = (next_q_values * gamma) + rewards
                
                loss = F.mse_loss(current_q_values, target_q_values.unsqueeze(1))
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                
            if em.done:
                episode_durations.append(episode_rewards)
                # plot(episode_durations, 100)
                break
                
            
            em.env.screen.clear()
        if episode % target_update == 0:
            target_net.load_state_dict(policy_net.state_dict())
if __name__ == '__main__':
    main()
        























                

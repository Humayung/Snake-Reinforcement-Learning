import gym
import numpy as np
import torch
import torchvision.transforms as T
from Snake_env import Snake

class SnakeEnvManager():
    def __init__(self, device):
        self.device = device
        self.env = Snake(30, 30)
        self.env.reset()
        self.current_screen = None
        self.done = False
        
    def reset(self):
        self.env.reset()
        self.current_screen = None
        
    def close(self):
        self.env.close()
        
    def render(self, mode='human'):     
        return self.env.render(mode)
        
    def num_actions_available(self):
        return self.env.action_space.n
    
    def take_action(self, action):
        _, reward, self.done, _ = self.env.step(action.item())
        return torch.tensor([reward], device=self.device)
    
    def just_starting(self):
        return self.current_screen is None
    
    def get_state(self):
        if self.just_starting() or self.done:
            self.current_screen = self.get_processed_screen()
            black_screen = torch.zeros_like(self.current_screen)
            return black_screen
        else:
            s1 = self.current_screen
            s2 = self.get_processed_screen()
            self.current_screen = s2
            return s2
            
    def get_screen_height(self):
        screen = self.get_processed_screen()
        return screen.shape[2]
        
    def get_screen_width(self):
        screen = self.get_processed_screen()
        return screen.shape[3]
        
    def get_processed_screen(self):
        # screen = self.render('rgb_array').transpose((2, 0, 1))
        self.render('rgb_array')
        screen = self.env.get_view(0.65).transpose((2, 0, 1))
        return self.transform_screen_data(screen)
        
    def crop_screen(self, screen):
        screen_height = screen.shape[1]
        
        top = int(screen_height * 0.4)
        bottom = int(screen_height * 0.8)
        screen = screen[:, top:bottom, :]
        return screen
        
    def transform_screen_data(self, screen):
        screen = np.ascontiguousarray(screen, dtype=np.float32) / 255
        screen = torch.from_numpy(screen)
        
        resize = T.Compose([
            T.ToPILImage(),
            T.ToTensor()
        ])
        
        return resize(screen).unsqueeze(0).to(self.device)

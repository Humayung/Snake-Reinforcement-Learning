import torch
import torch.nn as nn
import torch.nn.functional as F
class DQN(nn.Module):
    def __init__(self, img_height, img_width):
        super().__init__()
        self.fc1 = nn.Linear(in_features=img_height * img_width, out_features=25)
        self.fc2 = nn.Linear(in_features=25, out_features=32)
        self.out = nn.Linear(in_features=32, out_features=4)
        
    def forward(self, t):
        t = t.flatten(start_dim=1)
        t = F.relu(self.fc1(t))
        t = F.relu(self.fc2(t))
        t = self.out(t)
        return t

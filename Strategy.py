import math

class EpsilonGreedyStrategy():
    epsilon = 0
    def __init__(self, start, end, decay):
        self.start = start
        self.end = end
        self.decay = decay
    
    def get_exploration_rate(self, current_step):
        self.epsilon = self.end + (self.start - self.end) * math.exp(-1. * current_step * self.decay)
        return self.epsilon

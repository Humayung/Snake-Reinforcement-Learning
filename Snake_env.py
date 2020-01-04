from sty import Style, RgbFg, fg,bg, ef, rs
from random import randint
from ScreenManager import Screen
import numpy as np

class Action():
    n = 4

class Snake:

    def __init__(self, width, height):
        self.action_space = Action()
        self.screen = Screen()
        self.screen.size(width, height)
        screen = self.screen
        self.avDir = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        self.currentDir = 0
        
        # State Dict
        self.BODY_COLOR = screen.color('fill', 255, 255, 255)
        self.BORDER_COLOR = screen.color('fill', 255, 255, 255)
        self.HEAD_COLOR = screen.color('fill', 0, 0, 255)
        self.BLANK_COLOR = 0
        self.APPLE_COLOR = screen.color('fill', 255, 100, 0)
        # self.STATE_ID = {self.HEAD_COLOR: [0, 0, 255], self.BODY_COLOR : [255, 255, 255], self.BORDER_COLOR : [255, 255, 255], self.BLANK_COLOR : [0, 0, 0], self.APPLE_COLOR : [255, 127, 0]}        
        self.STATE_ID = {self.HEAD_COLOR: 1, self.BODY_COLOR : 1, self.BORDER_COLOR : 1, self.BLANK_COLOR : 0, self.APPLE_COLOR : 0.5}        
        self.borderShape = {'x' : 0, 'y' : 0, 'w' : self.screen.WIDTH, 'h' : self.screen.HEIGHT}
        self.textPos = [self.borderShape.get('x') + self.borderShape.get('w') - 2, self.borderShape.get('x') + self.borderShape.get('w')]
        self.screen.fillText(255, 255, 0)
        self.reset()

    def reset(self):
        self.steps_without_scoring = 0
        self.createGame(3)
        self.score = 0
        self.spawnApple(self.borderShape)
        self.updateMatrix()
    
    def createGame(self, length):
        self.matrix = [0 for i in range(self.borderShape.get('w') * self.borderShape.get('h'))]
        self.body = []
        for i in range(length):
            x = (self.borderShape.get('x')) + self.borderShape.get('w')//2 + i
            y = (self.borderShape.get('y')) + self.borderShape.get('h')//2
            self.body.append(self.screen.getIndex(x, y))
        self.generateStaticBorder(self.borderShape)
    
    def get_view(self, field):
        self.stateSize = int(self.screen.WIDTH * field)
        head_i = self.body[0]
        head_x = head_i % self.screen.WIDTH;
        head_y = head_i // self.screen.WIDTH;

        state = np.zeros([self.stateSize, self.stateSize])
        
        rX = self.borderShape.get('x')
        rY = self.borderShape.get('y')
        rW = self.borderShape.get('w')
        rH = self.borderShape.get('h')

        for i in range(self.stateSize):
            y = i - self.stateSize // 2 + head_y
            for j in range(self.stateSize):
                index = i + j * self.stateSize
                x = j - self.stateSize // 2 + head_x
                if x >= rX and x < rX + rW and y >= rY and y < rY + rH:
                    m_index = x + y * self.screen.WIDTH
                    state[i][j] = self.STATE_ID.get(self.matrix[m_index])
                else:
                    state[i][j] = self.STATE_ID.get(self.BORDER_COLOR)
        return state
        
    def get_screen(self):
        state = np.zeros([self.screen.WIDTH, self.screen.HEIGHT])
        for i in range(state.shape[0]):
            for j in range(state.shape[1]):
                index = i + j * self.screen.WIDTH
                state[i][j] = self.STATE_ID.get(self.matrix[index])
        return state

    def updateMatrix(self):
        for index in self.body:
            self.matrix[index] = self.BODY_COLOR  
        self.matrix[self.apple] = self.APPLE_COLOR
        self.matrix[self.body[0]] = self.HEAD_COLOR      

    def generateStaticBorder(self, borderLoc):
        x = borderLoc.get('x')
        y = borderLoc.get('y')
        w = borderLoc.get('w')
        h = borderLoc.get('h')
        # Rectangle
        for i in range(x, x + w):
            self.matrix[i + y * self.screen.WIDTH] = self.BORDER_COLOR
            self.matrix[(h - 1 + y) * self.screen.WIDTH + i] = self.BORDER_COLOR
        
        for i in range(y, y + h):
            self.matrix[x + i * self.screen.WIDTH] = self.BORDER_COLOR
            self.matrix[x + i * self.screen.WIDTH + w - 1] = self.BORDER_COLOR

    def render(self, mode="rgb-array"):
        self.screen.clear()
        self.screen.put(self.matrix)
        scoreText = '%04d' % self.score
        self.screen.text(scoreText, self.textPos[0], self.textPos[1])
        return self.get_screen()

    def evaluateDir(self, dir):
        currentDir = self.currentDir
        if currentDir == 0:
            if dir == 1:
                 return currentDir
            return dir
        if currentDir == 1:
            if dir == 0:
                 return currentDir
            return dir 
        if currentDir == 2:
            if dir == 3:
                 return currentDir
            return dir
        if currentDir == 3:
            if dir == 2:
                 return currentDir
            return dir
    
    def spawnApple(self, borderLoc):
        new_loc = 0
        try:
            new_loc = randint(0, len(self.matrix) - 1)
            while self.matrix[new_loc] is not 0 :
                new_loc = randint(0, len(self.matrix) - 1)
        except:
            print(new_loc)
        self.apple = new_loc
    
    def anApple(self, head):
        return head == self.apple
    
    def aBorder(self, head):
        return self.matrix[head] == self.BORDER_COLOR
    
    def grow(self):
        self.score += 1
        self.body.append(0)
    
    def make_action(self, dir):
        # Make sure the snake does not collapse into its body
        self.currentDir = self.evaluateDir(dir)
        
        # Dont bother to type 'self'
        body = self.body
        screen = self.screen
        
        # Shift body
        blockTail = body[-1]
        body.insert(0, body[0]);
        body.pop(-1);
        
        # Shift Head
        head = screen.getCoor(body[0])
        head = head + self.avDir[self.currentDir]
        body[0] = screen.getIndex(head)

        # Remove Tail
        self.matrix[blockTail] = self.BLANK_COLOR   
        
        done = False
        if self.aBorder(body[0]):
            done = True
        
        if self.anApple(body[0]):
            self.grow()
            self.spawnApple(self.borderShape)
            
        self.updateMatrix()
        return done
        
    def step(self, dir):
        score_before = self.score
        done = self.make_action(dir)
        score_after = self.score
        reward = score_after - score_before
        
        if reward == 0:
            self.steps_without_scoring += 1
        else:
            self.steps_without_scoring = 0
        
        if self.steps_without_scoring > 300:
            done = True
            
        
        return (None, reward, done, None)
    
        

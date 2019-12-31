from os import system, name 
from time import sleep 
import numpy as np
from sty import Style, RgbBg, fg, bg, ef, rs


class Screen:
    WIDTH = 85
    HEIGHT = 37
        
    def __init__(self):
        self.isLooping = True
        self.length = self.WIDTH * self.HEIGHT
        self.fillColor = self.color('fill', 255, 255, 255)
        self.textColor = self.color('text', 255, 255, 255)
        self.delay = 1/60.0
        
    def drawPoint(self, x, y):
        x *= 2
        x += 1
        y += 1
        print("\033[" + str(y) + ";" + str(x) + "H" + self.fillColor + "  \x1b[49m")
      
    def clear(self): 
        system('clear')     
        
    def fill(self, *args):
        if len(args) == 1:
            self.fillColor = args[0]
        else:
            self.fillColor = self.color(args[0], args[1],args[2])  

    def setup(self):
        pass
    
    def fillText(self, r, g, b):
        self.textColor = self.color('text', r, g, b)
        
    def size(self, width, height):
        Screen.WIDTH = width
        Screen.HEIGHT = height

    def text(self, letter, x, y):
        print("\033[" + str(y) + ";" + str(x) + "H" + self.textColor + str(letter) + '\x1b[39m')

    def color(self, mode, r, g, b):
        if mode == 'fill':
            return '\x1b[48;2;' + str(r) + ';' + str(g) + ';' + str(b) + 'm'
        return '\x1b[38;2;' + str(r) + ';' + str(g) + ';' + str(b) + 'm'
        

    def getCoor(self, index):
        x = index % self.WIDTH
        y = index // self.WIDTH
        return np.array([x, y])
    
    def getIndex(self, *args):
        if len(args) == 1:
            return args[0][0] + args[0][1] * self.WIDTH 
        return args[0] + args[1] * self.WIDTH

    def put(self, pixels):
        for i in range(len(pixels)):
            pixel = pixels[i]
            if pixel is not 0:
                self.fill(pixel)
                coor = self.getCoor(i)
                self.drawPoint(coor[0], coor[1])

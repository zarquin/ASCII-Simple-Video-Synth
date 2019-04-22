"""
helper file for ascii art synth generation.

"""
import time, os

def col255_from_RGB(red,green,blue):
    """ returns a term256 colour index from RGB value
       found at :
       https://unix.stackexchange.com/questions/269077/
    """
    if red > 255:
        red = 255
    if green > 255:
        green = 255
    if blue > 255:
        blue = 255

    if red < 75:
        red = 0
    else:
        red = ((red -35)/40)
        red = red*6*6
    if green < 75:
        green = 0
    else:
        green = ((green - 35)/40)
        green = green*6
    if blue<75:
        blue = 0
    else:
        blue = ((blue -35)/40)
    j = int(red+green+blue+16)

    if j>255:
        j=255
    return j 

def char_count(screen):
    return screen.dimensions[0]*screen.dimensions[1]

def char_index_to_YX(screen, index):
    maxtup = screen.dimensions
    maxval = char_count(screen)
    if(index>maxval):
        index = maxval
    if(index <0):
        index = 0
    lines = int(index / maxtup[1])
    cols = index % maxtup[1]
    return ( lines, cols)

class Generator:
    def __init__(self, shape, increment, scale):
        self.shape = shape
        self.increment = increment
        self.value = 0.0
        self.wrap = 1.0
        self.scale = scale
        return
    def reset(self, new_value=0):
        self.value = new_value
        return
    def next(self):
        self.value +=self.increment
        if self.value>self.wrap:
            self.value = (self.value - self.wrap)
        if self.value < 0.0:
            self.value =0.0
        return (self.value*self.scale)

    def set_increment(self, new_increment):
        self.increment = new_increment
        return
    def set_scale(self, new_scale):
        self.scale = new_scale
        return



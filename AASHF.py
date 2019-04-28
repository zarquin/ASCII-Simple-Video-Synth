"""
helper file for ascii art synth generation.
zarquin@ucc.asn.au
(c) 2019
See LICENSE for licence details
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
    #modes
    # 0 freerun
    # 1 reset on line
    # 2 reset on frame
    # 3 oneshot, hold at 0 reset on line
    # 4 oneshot, hold at 0 reset on frame
    # 5 oneshot, hold at 1, rest on line
    # 6 oneshot, hold at 1, reset on frame
    def __init__(self, shape, increment=0.01, scale=255, offset=0,mode=0):
        self.shape = shape
        self.increment = increment
        self.value = 0.0
        self.wrap = 1.0
        self.scale = scale
        self.offset = offset
        self.mode = mode
        self.run = True
        return

    def reset(self, new_value=0):
        self.value = new_value
        self.run=True
        return

    def get_shaped_value(self):
        if self.value < self.shape:
            return self.value / self.shape
        else:
            shaped = 1 - ((self.value - self.shape)* ( 1. / (1.-self.shape) ) )
            return shaped
    
    def calculate_and_limit(self):
        ret_val = 0
        ret_val = int(self.value * self.scale)
        ret_val = ret_val+self.offset
        if ret_val > 255:
            ret_val = 255
        if ret_val <0:
            ret_val = 0
        return ret_val

    def next(self):

        if self.run is False:
        # if we're in a "oneshot" mode return the current value.
            return self.calculate_and_limit()
        self.value +=self.increment
        if self.value>self.wrap:
            self.value = (self.value - self.wrap)
            #if we're in oneshot mode, we need to do logic here.
            if self.mode in [3,4]:  #oneshot return to 0.0
                self.value = 0.0
                self.run = False
            if self.mode in [5,6]:  #oneshot hold at 1.0
                self.value = 1.0
                self.run = False
        if self.value > self.wrap:
            #stop it blowing up
            self.value = 0.0
        if self.value < 0.0:
            self.value =0.0  
        return self.calculate_and_limit()

    def set_mode(self, new_mode):
        new_mode = int(new_mode)
        if new_mode > 6:
            new_mode = 6
        if new_mode < 0:
            new_mode = 0
        self.mode = new_mode
        return

    def line_reset(self):
        if self.mode in [1,3,5]:
            self.run = True
            self.reset(0.0)
        return

    def frame_reset(self):
        if self.mode in [2,4,6]:
            self.run = True
            self.reset(0.0)
        return

    def set_offset(self,new_offset):
        new_offset = int(new_offset)
        if new_offset > 255:
            new_offset = 255
        if new_offset <0:
            new_offset = 0
        self.offset = new_offset
        return

    def set_increment(self, new_increment):
        #increment has to be less than 2.0
        if new_increment > 1.9:
            new_increment = 1.9
        self.increment = new_increment
        return

    def set_scale(self, new_scale):
        new_scale = int(new_scale)
        if new_scale > 255:
            new_scale = 255
        if new_scale <0:
            new_scale = 0
        self.scale = new_scale
        return



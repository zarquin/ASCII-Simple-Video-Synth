"""
helper file for ascii art synth generation.
zarquin@ucc.asn.au
(c) 2019
See LICENSE for licence details
"""
import time, os, math

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

# The following 4 methods are taken/adapted from:
# https://stackoverflow.com/questions/41644778/convert-24-bit-color-to-4-bit-rgbi

# find the closest RGBx approximation of a 24-bit RGB color, for x = 0 or 1
def rgbx_approx(red, green, blue, x):
    threshold = (x + 1) * 255 / 3
    r = 1 if (red > threshold) else 0
    g = 1 if (green > threshold) else 0
    b = 1 if (blue > threshold) else 0
    return (r, g, b)

# convert a 4-bit RGBI color back to 24-bit RGB
def rgbi_to_rgb24(r, g, b, i):
   red = (2*r + i) * 255 / 3
   green = (2*g + i) * 255 / 3
   blue = (2*b + i) * 255 / 3
   return (red, green, blue)


# return the (squared) Euclidean distance between two RGB colors
def color_distance(red_a, green_a, blue_a, red_b, green_b, blue_b):
   d_red = red_a - red_b
   d_green = green_a - green_b
   d_blue = blue_a - blue_b
   return (d_red * d_red) + (d_green * d_green) + (d_blue * d_blue)

# find the closest 4-bit RGBI approximation (by Euclidean distance) to a 24-bit RGB color
def col15_from_RGB(red, green, blue):
    # find best RGB0 and RGB1 approximations:
    (r0, g0, b0) = rgbx_approx(red, green, blue, 0);
    (r1, g1, b1) = rgbx_approx(red, green, blue, 1);

    # convert them back to 24-bit RGB:
    (red0, green0, blue0) = rgbi_to_rgb24(r0, g0, b0, 0);
    (red1, green1, blue1) = rgbi_to_rgb24(r1, g1, b1, 1);

    # return the color closer to the original:
    d0 = color_distance(red, green, blue, red0, green0, blue0);
    d1 = color_distance(red, green, blue, red1, green1, blue1);
    out = 0
    rgbi = [r0, g0, b0, 0] if (d0 <= d1) else [r1, g1, b1, 1]
    for bit in rgbi:
        out = (out << 1) | bit
    return out

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
    def __init__(self, shape=0.5, increment=0.01, scale=255, offset=0,mode=0):
        self.shape = shape
        self.increment = increment
        self.value = 0.0
        self.wrap = 1.0
        self.scale = scale
        self.offset = offset
        self.mode = mode
        self.run = True
        self.last_value = 0.0
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
        ret_val = int(self.get_shaped_value() * self.scale)
        ret_val = ret_val+self.offset
        if ret_val > 255:
            ret_val = 255
        if ret_val <0:
            ret_val = 0
        self.last_value = ret_val
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

    def set_increment_8bit(self,new_increment):
        # this is for setting the increment using a 0-255 bit value.
        if new_increment > 255:
            new_increment = 255
        if new_increment < 0:
            new_increment = 0

        new_increment+=1
        jif = math.log(new_increment,256)
        jif = abs(jif)
        self.increment = jif
        return

        
    def set_shape_8bit(self, new_shape):

        if new_shape > 255:
            new_shape = 255
        if new_shape < 0:
            new_shape = 0
        
        self.shape = new_shape / 255.0
        if self.shape >=1.0:
            self.shape =0.999
        return



    def set_increment(self, new_increment):
        #increment has to be less than 2.0

        #increment value of 255 = 1.0
        #increment value of 0 = 1.0/(chart_count*2)

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



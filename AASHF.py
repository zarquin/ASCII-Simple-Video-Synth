"""
helper file for ascii art synth generation.
zarquin@ucc.asn.au
(c) 2019
See LICENSE for licence details
"""
import time, os, math
#from fastnumbers import int, fast_int

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

class ShapePoints:
    #this method creats a multipoint polygon using two sinewave generators.
    # Lissajous method.
    # the points are evenly selected from around the time.  e.g. the points are from 0 -> 2Pi.
    # x = sine(t + starting_offset) etc.
    # the starting offset will allow for a nice rotation frame to frame.

    def __init__(self, sides=3, xincrement=0.01, size=0.5, yincrement=0.01, screen_x=80, screen_y=24):
        self.size=size
        self.sides=sides
        self.xincrement=xincrement
        self.yinrement=yincrement
        self.mode = 0
        self.run=True
        self.lastx = 0.0
        self._xvalue = self.lastx
        self.lasty = 0.0
        self._yvalue = self.lasty
        self.noise = 0.0
        self.screen_x = screen_x
        self.screen_y = screen_y
        self.centre_x = screen_x/2
        self.centre_y = screen_y/2
        self.shape_count = 1
        self.shape_space = 0
        return
    
    def saw_to_tri(self, arg_val):
        # -2 to -1 is 0 -> -1 counting down.  
        # -1 to +1 is counting up.
        # +1 to +2 is +1 -> 0 counting down.
        if arg_val > 2.0:
            arg_val = 2.0
        if arg_val < -2.0:
            arg_val = -2.0

        if arg_val < -1.0:
            return( -1.0 - arg_val)
        if arg_val > 1.0:
            return ( 1.0 - (arg_val -1.0)  )

        return arg_val

    def render_to_screen(self, the_screen, cf, cb):
        #cf is colour foreground, 
        # cb is colour background.
        for i in range(self.shape_count):
            the_screen.fill_polygon( [self.get_points()], colour=cf, bg=cb )
            for j in range(self.shape_space):
                self.update_points()


    def update_points(self):
        #this is a dumb triangle wave oscillator 
        # output is -1 to +1.
        # rather than having a private variable for direction, we will count as a sawtooth from -2 to +2
        # -2 to -1 is 0 -> -1 counting down.  
        # -1 to +1 is counting up.
        # +1 to +2 is +1 -> 0 counting down.
        # when gets to +2 resets to -2
        self._xvalue += self.xincrement
        if self._xvalue > 2.0:
            self._xvalue = self._xvalue - 4.0
        self._yvalue += self.yinrement
        if self._yvalue > 2.0:
            self._yvalue = self._yvalue - 4.0
        
        self.lastx = self.saw_to_tri(self._xvalue)
        self.lasty = self.saw_to_tri(self._yvalue)

    def points_to_screen_locations(self):
        #this returns an x y tuple in relation to the size of the screen
        xc = self.centre_x
        yc = self.centre_y

        max_x = int((self.screen_x/2) * self.size )
        max_y = int((self.screen_y/2) * self.size )

        xc = int(max_x*self.lastx + xc)
        yc = int(max_y*self.lasty + yc)

        #could put in bounds checking here.  i don't want to to see what it does.
        return (xc, yc)

    def get_points(self):
        #this method returns an array of x,y tuples
        #the number of points is based on the sides variable.
        ret_val = [] #empty dictionary
        for j in range(self.sides):
            self.update_points()
            ret_val.append(self.points_to_screen_locations())
        return ret_val

    def set_shape_count8bit(self, new_value):
        if new_value  > 255:
            new_value = 255
        if new_value <0:
            new_value = 0
        self.shape_count = int(new_value/25)
        return
    
    def set_shape_space8bit(self, new_value):
        if new_value > 255:
            new_value = 255
        if new_value < 0:
            new_value = 0
        
        self.shape_space = int( new_value/50)
        return

    def set_xincrement8bit(self, new_inc):
        
        incval = new_inc/ 127.0
        self.set_xincrement(incval)
        return

    def set_centerx8bit(self, new_value):
        if new_value < 0 :
            new_value = 0
        if new_value > 255:
            new_value = 255
        self.centre_x = int( self.screen_x* new_value/255)
        return
    
    def set_centery8bit(self, new_value):
        if new_value < 0 :
            new_value = 0
        if new_value > 255:
            new_value = 255
        self.centre_y = int( self.screen_y* new_value/255)
        return


    def set_xincrement(self, new_xinc):      
        if new_xinc < 0:
            new_xinc = 0
        if new_xinc > 2.0:
            new_xinc = 2.0
        self.xincrement = new_xinc
        return

    def set_yincrement8bit(self, new_inc):
        
        incval = new_inc/ 127.0
        self.set_yincrement(incval)
        return

    def set_yincrement(self, new_yinc):
        if new_yinc > 2.0:
            new_yinc = 2.0
        if new_yinc < 0:
            new_yinc = 0
            
        self.yinrement = new_yinc
        return


    def set_size8bit(self, newval):
        size = newval/255.0
        self.size = size
        return

    def set_size(self, new_size, screen_x, screen_y):
        # a size of 1 = either height/2 or width/2 as this is 
        # currently based around a centre of the screen point.
        if new_size <0:
            new_size = 0.0
        if new_size > 1.0:
            new_size = 1.0
        self.size = new_size
        self.screen_x = screen_x
        self.screen_y = screen_y
        return

    def set_sides8bit(self, newsides):
        # 0 = 3
        # 255 = 10
        # 0 = 0 255=7
        # +3 
        newsides = newsides/35
        newsides +=3
        self.set_sides(newsides)
        return

    def set_sides(self, new_sides):
        #set the number of sides on the shapes.
        # less than 3 is a bit silly.  more than 10 is also probably a bit hard.
        new_sides = int(new_sides)
        if new_sides <3:
            new_sides = 3
        if new_sides > 10:
            new_sides = 10
        self.sides = new_sides
        return

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
        self.invert = False
        return

    def nudge(self, nudge_value):
        #nudge is meant to be for small value changes. 0.01 and smaller. we won't do any checking here though.
        self.increment=self.increment+float(nudge_value)
        return

    def set_invert(self):
        self.invert=True
        return
    def clear_invert(self):
        self.invert=False
        return

    def reset(self, new_value=0):
        self.value = new_value
        self.run=True
        return
 #   @profile
    def get_shaped_value(self):
        if self.value < self.shape:
            return self.value / self.shape
        else:
            return (1. - ((self.value - self.shape)/ (1.-self.shape) ))
 #           shaped = 1 - ((self.value - self.shape)* ( 1. / (1.-self.shape) ) )
 #           return shaped
    
 #   @profile
    def calculate_and_limit(self):
        #ret_val = 0
        #ret_val = int(self.get_shaped_value() * self.scale)+self.offset
        aa = self.get_shaped_value() * self.scale
        #ret_val = fast_int(aa, raise_on_invalid=True) + self.offset
        ret_val = int(aa)+self.offset
        #ret_val = ret_val+self.offset
        #If we're inverting, do it here.
        if self.invert:
            ret_val = 255-ret_val
        if ret_val > 255:
            ret_val = 255
        if ret_val <0:
            ret_val = 0
        self.last_value = ret_val
        return ret_val

   # @profile
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

    def set_increment_9bit(self, new_increment):
        if new_increment > 512:
            new_increment = 512
        if new_increment < 0:
            new_increment = 0.001

        #new_increment+=1.
        #jif = math.log(new_increment,512)
        jif = new_increment/512.
        jif = abs(jif)
        self.increment = jif
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



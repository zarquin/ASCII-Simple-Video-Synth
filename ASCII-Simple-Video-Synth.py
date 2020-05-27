"""
ASCII-Simple-Video-Synth
A simple ASCII terminal code video synth. 
zarquin@ucc.asn.au
(c) 2019
See LICENSE for licence details
"""


from asciimatics.screen import Screen
import asciimatics
import AASHF
from AASHF import Generator, ShapePoints
from pythonosc import dispatcher
from pythonosc import osc_server
import time
import threading
import sys
from random import randint
import cProfile
import code

import argparse

redGen = Generator(0.1,0.01,255.0)
bluGen = Generator(0.3,0.002,255.0)
grnGen = Generator(0.5,0.001,255.0)

avgGrn = 0
avgRed = 0
avgBlu = 0

debug = False
verbose = False

shape_drawer = ShapePoints(sides=4, xincrement=0.7, yincrement=0.999, size=0.7)

single_draw_delay = False
strobe_mode = False
strobe_colour = Screen.COLOUR_WHITE
#frame_time=30

def global_strobe_handler(unused_addr, args, val):
    global strobe_mode, strobe_colour
    strobe_mode=True
    value = int(val)
    if value > 255 or value < 0:
        value = randint (0,255)
    strobe_colour = value
    return

def speed_handler(unused_addr, args, val):
    value = int(val)/240.0
    args[0](value)
    return

def standard_handler(unused_addr, args, val):
    value = int(val)
    args[0](value)
    return

#@profile
def get_colour():
    global avgBlu, avgGrn, avgRed
    red = int(redGen.next() )
    green = int (grnGen.next() )
    blue = int(bluGen.next() )
    
    #update the average values
    avgBlu = (avgBlu + blue )/2
    avgGrn = (avgGrn+ green)/2
    avgRed = (avgRed + red)/2
    
    if sys.platform == "win32":
        return AASHF.col15_from_RGB(red, green, blue)
    else:
        return AASHF.col255_from_RGB(red,green,blue)


def frame_reset():
    redGen.frame_reset()
    grnGen.frame_reset()
    bluGen.frame_reset()
    return

def line_reset():
    redGen.line_reset()
    grnGen.line_reset()
    bluGen.line_reset()
    return

def reset_average():
    global avgBlu, avgGrn , avgRed
    avgBlu = 0
    avgGrn = 0
    avgRed = 0

def get_compliment_of_average():
    #convert average to HSI
    # we want a high contrast colour for the shape.
    # and then a complimentary value for the bg for the shape.

    # temporary colour values 
    tr=255
    tb=255
    tg =255

    if avgRed > 126:
        tr = 0
    if avgBlu > 126:
        tb = 0
    if avgGrn > 126:
        tg = 0
    
    if tg+tb+tr > 382:
        bg = Screen.COLOUR_BLACK
    else: 
        bg = Screen.COLOUR_WHITE
    fg = 0
    if sys.platform == "win32":
      fg = AASHF.col15_from_RGB(tr, tg, tb)
      fg = fg >> 1
    else:
      fg = AASHF.col255_from_RGB(tr, tg, tb)
    return (fg , bg)

def draw_strobe(screen):
    global single_draw_delay, strobe_colour, strobe_mode
    #frame_reset()
    for i in range( AASHF.char_count(screen)):
        bg = strobe_colour
        YX = AASHF.char_index_to_YX(screen, i)
        attr=0
        screen.print_at(" ", YX[1], YX[0],colour=7, attr=attr, bg=bg)
    screen.refresh()
    #time.sleep(2.0)
    strobe_mode=False
    return

#@profile

def draw_scene2(screen):
    #refactor to see if writing line-by-line is more performant
    global single_draw_delay, strobe_colour, strobe_mode
    reset_average()
    frame_reset()
    for i in range (screen.height): #get line count):
        line_reset()
        cm=[] #new empty list for colour_map
        st="" #new empty string
        for j in range (screen.width): #get width):
            this_pixel = get_colour()
            ch=''
            if draw_foreground:
                fg=this_pixel
                attr=0
                bg=0
                ch="\u2588"
            else:
                bg=this_pixel
                attr=0
                fg=7
                ch=" "
            cm.append( (fg,attr,bg))
            st=''.join((st,ch))
        screen.paint(st, 0,i, colour_map= cm) 

    ss = shape_drawer.size
    shape_drawer.set_size(new_size=ss, screen_x=screen.width, screen_y=screen.height)
    (cf, cb) = get_compliment_of_average()
    shape_drawer.render_to_screen(screen, cf, cb)
    screen.refresh()
    return

def draw_scene(screen):
    global single_draw_delay, strobe_colour, strobe_mode, draw_foreground
    reset_average()
    frame_reset()
    for i in range( AASHF.char_count(screen)):
        this_pixel = get_colour()
        YX = AASHF.char_index_to_YX(screen, i)
        if YX[1] == 0:
            line_reset()
        bg = this_pixel
        attr = 0
        if sys.platform == "win32":
            # on Windows, this_pixel is a 4 bit colour index value
            # we need to extract both the colour value and intensity separately
            bg = this_pixel >> 1
            attr = this_pixel & 1
        if draw_foreground:
            screen.print_at("\u2588",YX[1], YX[0], colour=bg)
        else:
            screen.print_at(" ", YX[1], YX[0],colour=7, attr=attr, bg=bg)
        if single_draw_delay:
            add_debug_info(screen)
            add_single_debug_info(screen, this_pixel, YX)
            screen.refresh()
            time.sleep(0.2)

    ss = shape_drawer.size
    shape_drawer.set_size(new_size=ss,screen_x = screen.width, screen_y=screen.height)
    (cf, cb) = get_compliment_of_average()
    shape_drawer.render_to_screen(screen, cf, cb)
    
    #if we're drawing a single pixel at a time, once we've drawn the screen, stop.
    if single_draw_delay:
        single_draw_delay = False

    screen.refresh()
    return

def add_single_debug_info(screen, pixel_value, XY):
    text_str = "colour {:3} R: {:3} G:{:3} B:{:3} X: {:3} Y: {:3} ".format(pixel_value, 
                                redGen.last_value, grnGen.last_value, bluGen.last_value, XY[1], XY[0])
    screen.print_at(text_str, 0, screen.height-4 ,colour=7 )
    return

def add_debug_info(screen):
    global framerate
    i=1
    egw = ["red","grn","blu"]
    ee = [redGen, grnGen,  bluGen ]
    ss="x:{:+2.2f} xi:{:+1.2f} y:{:+2.2f} yi:{:+1.2f} sze {:.2f} sds {} fr {:.1f}".format(shape_drawer.lastx, shape_drawer.xincrement,
                            shape_drawer.lasty, shape_drawer.yinrement,
                            shape_drawer.size, shape_drawer.sides, framerate )
    screen.print_at(ss, 0 , screen.height-4,colour=7)

    for q in range(3):
        j = ee[q]
        text_str = "{} val: {:.4f} inc: {:.3f} shp: {:.2f} mde: {:1} scl: {:3} off: {:3}".format(egw[q],j.value, 
                                                                            j.increment, j.shape, j.mode, j.scale, j.offset)
        screen.print_at(text_str, 0, screen.height-i ,colour=7 )
        i+=1
    screen.refresh()
    return

def ds(screen):
    #this is the main execution loop.
    # it controls the main outside loop and also reads the keys
    global verbose
    #verbose = False
    runrun = True
    global debug
    #debug = False
    global single_draw_delay, strobe_mode, frame_time, framerate
    global draw_method, draw_foreground
    single_draw_delay = False
    framerate=1.0

    while True:
        time_frame_start = time.time()
        if runrun:
            if strobe_mode:
                draw_strobe(screen)
                strobe_mode = False
            else:
                if draw_method==1:
                    draw_scene(screen)
                else:
                    draw_scene2(screen)
            if debug:
                runrun = False
        if verbose:
            add_debug_info(screen)

        ev = screen.get_key()
        
        if ev in (ord('v'), ord('V')):
            if verbose:
                verbose = False
            else:
                verbose = True
        
        if ev in (ord('S'), ord('s')):
            single_draw_delay = True
            runrun = True

        if ev in (ord('Q'), ord('q')):
            return

        if ev in (ord('d'), ord('D')):
            if debug:
                debug=False
            else:
                debug=True
        if ev in (ord('f'), ord('F')):
            runrun = True
        
        time_delta = (time.time()-time_frame_start)
        if(time_delta < frame_time):
            diff = frame_time - time_delta
            time.sleep(diff)
        
        framerate = 1.0/(time.time() - time_frame_start)
        #time.sleep(0.02)
    return



def setup_OSC(new_ip, new_port):
    disp = dispatcher.Dispatcher()
    disp.map("/red/mode",standard_handler, redGen.set_mode)
    disp.map("/green/mode",standard_handler, grnGen.set_mode)
    disp.map("/blue/mode",standard_handler, bluGen.set_mode)
    disp.map("/red/offset", standard_handler, redGen.set_offset)
    disp.map("/red/scale", standard_handler, redGen.set_scale)
    disp.map("/green/offset", standard_handler, grnGen.set_offset)
    disp.map("/green/scale", standard_handler, grnGen.set_scale)
    disp.map("/blue/offset", standard_handler, bluGen.set_offset)
    disp.map("/blue/scale", standard_handler, bluGen.set_scale)
    disp.map("/blue/shape", standard_handler, bluGen.set_shape_8bit)
    disp.map("/green/shape", standard_handler, grnGen.set_shape_8bit)
    disp.map("/red/shape", standard_handler, redGen.set_shape_8bit)
    disp.map("/red/speed",speed_handler,redGen.set_increment_8bit)
    disp.map("/green/speed",speed_handler,grnGen.set_increment_8bit)
    disp.map("/blue/speed",speed_handler,bluGen.set_increment_8bit)
    disp.map("/shape/sides", standard_handler, shape_drawer.set_sides8bit)
    disp.map("/shape/size", standard_handler, shape_drawer.set_size8bit)
    disp.map("/shape/xinc",standard_handler, shape_drawer.set_xincrement8bit)
    disp.map("/shape/yinc", standard_handler, shape_drawer.set_yincrement8bit)
    disp.map("/shape/xcenter", standard_handler, shape_drawer.set_centerx8bit)
    disp.map("/shape/ycenter", standard_handler, shape_drawer.set_centery8bit)
    disp.map("/shape/shapecount", standard_handler, shape_drawer.set_shape_count8bit)
    disp.map("/shape/shapeskip", standard_handler, shape_drawer.set_shape_space8bit)
    disp.map("/global/strobe", global_strobe_handler,"zz")

    server = osc_server.ThreadingOSCUDPServer(
            (new_ip,new_port), disp)
    server_thread = threading.Thread(target = server.serve_forever)
    server_thread.start()
    return server, server_thread

def main():
    global frame_time
    global debug
    global verbose
    global draw_method
    global draw_foreground
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--debug",action='store_true' , help="debug mode for Step")
    parser.add_argument("-v","--verbose",action='store_true' , help="display rendering information")
    parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=8000,
      help="The port the OSC server is listening on")  
    parser.add_argument("--framerate", type=int, default=30,
      help="the max framerate to use" )
    parser.add_argument("--drawmethod", type=int, default=1, 
        help="which draw process to use, 1 or 2")
    parser.add_argument("--foreground", action='store_true', help="draw colour in forground or background")
    
    args = parser.parse_args()
    frame_time = 1.0/args.framerate
    debug = args.debug
    verbose = args.verbose
    draw_method = args.drawmethod
    draw_foreground = args.foreground

    s = setup_OSC(args.ip, args.port)
    Screen.wrapper(ds)
    s[0].shutdown()
    quit()


if __name__ == "__main__":
    main()
    #cProfile.run(main())




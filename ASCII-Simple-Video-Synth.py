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
from AASHF import Generator
from pythonosc import dispatcher
from pythonosc import osc_server
import time
import threading
import sys

import argparse

redGen = Generator(0.1,0.01,255.0)
bluGen = Generator(0.3,0.002,255.0)
grnGen = Generator(0.5,0.001,255.0)

single_draw_delay = False


def speed_handler(unused_addr, args, val):
    value = int(val)/240.0
    args[0](value)
    return

def standard_handler(unused_addr, args, val):
    value = int(val)
    args[0](value)
    return


def get_colour():
    red = int(redGen.next() )
    green = int (grnGen.next() )
    blue = int(bluGen.next() )
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

def draw_scene(screen):
    global single_draw_delay
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
            screen.print_at(" ", YX[1], YX[0],colour=7, attr=attr, bg=bg)
        if single_draw_delay:
            add_debug_info(screen)
            add_single_debug_info(screen, this_pixel, YX)
            screen.refresh()
            time.sleep(0.2)
    
    #if we're drawing a single pixel at a time, once we've drawn the screen, stop.
    if single_draw_delay:
        single_draw_delay = False

    screen.refresh()
    return

def add_single_debug_info(screen, pixel_value, XY):
    text_str = "colour {:3} R: {:3} G:{:3} B:{:3} X: {:3} Y: {:3} ".format(pixel_value, 
                                redGen.last_value, grnGen.last_value, bluGen.last_value, XY[1], XY[0])
    screen.print_at(text_str, 0, screen.height-4 ,colour=7 )


def add_debug_info(screen):
    i=1
    egw = ["red","grn","blu"]
    ee = [redGen, grnGen,  bluGen ]
    for q in range(3):
        j = ee[q]
        text_str = "{} val: {:.4f} inc: {:.3f} shp: {:.2f} mde: {:1} scl: {:3} off: {:3}".format(egw[q],j.value, 
                                                                            j.increment, j.shape, j.mode, j.scale, j.offset)
        screen.print_at(text_str, 0, screen.height-i ,colour=7 )
        i+=1
    screen.refresh()
    return

def ds(screen):
    verbose = False
    runrun=True
    debug=False
    global single_draw_delay
    single_draw_delay = False

    while True:
        if runrun:
            draw_scene(screen)
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
        
        time.sleep(0.03)
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

    server = osc_server.ThreadingOSCUDPServer(
            (new_ip,new_port), disp)
    server_thread = threading.Thread(target = server.serve_forever)
    server_thread.start()
    return server, server_thread



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=8000,
      help="The port the OSC server is listening on")
    args = parser.parse_args()

    s = setup_OSC(args.ip, args.port)
    Screen.wrapper(ds)
    s[0].shutdown()
    quit()



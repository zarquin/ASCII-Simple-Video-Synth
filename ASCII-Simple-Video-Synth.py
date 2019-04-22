from asciimatics.screen import Screen
import asciimatics
import AASHF
from AASHF import Generator
from pythonosc import dispatcher
from pythonosc import osc_server
import time
import threading

import argparse

redGen = Generator(1.0,0.01,255.0)
bluGen = Generator(1.0,0.002,255.0)
grnGen = Generator(1.0,0.001,255.0)

red_offset = 80.0
green_offset = 0.0
blue_offset = 0.0

def red_speed_handler(unused_addr, args):
    value = int(args)/220.0
    redGen.set_increment(value)
    return

def green_speed_handler(unused_addr, args):
    value = int(args)/100.0
    grnGen.set_increment(value)
    return

def blue_speed_handler(unused_addr, args):
    value = int(args)/100.0
    bluGen.set_increment(value)
    return

def red_scale_handler(unused_addr, args):
    value=int(args)
    redGen.set_scale(value)
    return

def blue_scale_handler(unused_addr, args):
    value=int(args)
    bluGen.set_scale(value)
    return

def green_scale_handler(unused_addr, args):
    value=int(args)
    grnGen.set_scale(value)
    return

def red_offset_handler(unused_addr, args):
    value=int(args)
    global red_offset
    red_offset = value
    return

def blue_offset_handler(unused_addr, args):
    value=int(args)
    global blue_offset
    blue_offset = value
    return

def green_offset_handler(unused_addr, args):
    value=int(args)
    global green_offset
    green_offset = value
    return

def get_colour():
    red = int(redGen.next() + red_offset)
    green = int (grnGen.next() + green_offset)
    blue = int(bluGen.next() + blue_offset)

    return AASHF.col255_from_RGB(red,green,blue)

def draw_scene(screen):
    for i in range( AASHF.char_count(screen)):
        this_pixel = get_colour()
        YX = AASHF.char_index_to_YX(screen, i)
        screen.print_at(" ", YX[1], YX[0],colour=7, bg=this_pixel)
    screen.print_at("{} {} {} {} ".format(bluGen.value, redGen.value, grnGen.value, this_pixel), 0,0,colour=7)
    
    screen.print_at("{} {} {}".format(redGen.increment, redGen.scale, red_offset), 0,3,colour=7)
    
    screen.refresh()

def ds(screen):
    while True:
        draw_scene(screen)
        time.sleep(0.1)
    return

def setup_OSC():
    disp = dispatcher.Dispatcher()
    disp.map("/red/speed",red_speed_handler)
    disp.map("/red/offset", red_offset_handler)
    disp.map("/red/scale", red_scale_handler)
    disp.map("/green/speed",green_speed_handler)
    disp.map("/green/offset", green_offset_handler)
    disp.map("/green/scale", green_scale_handler)
    disp.map("/blue/speed",blue_speed_handler)
    disp.map("/blue/offset", blue_offset_handler)
    disp.map("/blue/scale", blue_scale_handler)

    server = osc_server.ThreadingOSCUDPServer(
            ("127.0.0.1",8000), disp)
    server_thread = threading.Thread(target = server.serve_forever)
    server_thread.start()



setup_OSC()
Screen.wrapper(ds)



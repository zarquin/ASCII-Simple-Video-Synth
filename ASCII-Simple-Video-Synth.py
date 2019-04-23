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

import argparse

redGen = Generator(1.0,0.01,255.0)
bluGen = Generator(1.0,0.002,255.0)
grnGen = Generator(1.0,0.001,255.0)


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
    frame_reset()
    for i in range( AASHF.char_count(screen)):
        this_pixel = get_colour()
        YX = AASHF.char_index_to_YX(screen, i)
        if YX[1] == 0:
            line_reset()
        screen.print_at(" ", YX[1], YX[0],colour=7, bg=this_pixel)
    screen.print_at("{:.2f} {:.2f} {:.2f} ".format(redGen.increment, grnGen.increment, bluGen.increment), 0,0,colour=7)
    screen.print_at("{} {} {} ".format(redGen.mode, grnGen.mode, bluGen.mode), 25,0,colour=7)
    
    #screen.print_at("{} {} {}".format(redGen.increment, redGen.scale, red_offset), 0,3,colour=7)
    
    screen.refresh()

def ds(screen):
    while True:
        draw_scene(screen)
        ev = screen.get_key()
        if ev in (ord('Q'), ord('q')):
            return
        time.sleep(0.1)
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

    disp.map("/red/speed",speed_handler,redGen.set_increment)
    disp.map("/green/speed",speed_handler,grnGen.set_increment)
    disp.map("/blue/speed",speed_handler,bluGen.set_increment)

    server = osc_server.ThreadingOSCUDPServer(
            (new_ip,new_port), disp)
    server_thread = threading.Thread(target = server.serve_forever)
    server_thread.start()
    return server, server_thread



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
    args = parser.parse_args()

    s = setup_OSC(args.ip, args.port)
    Screen.wrapper(ds)
    s[0].shutdown()
    quit()



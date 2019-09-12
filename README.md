# ASCII-Simple-Video-Synth
A simple video synth for Consoles, controlled by OSC
This is powered by the Asciimatics library.  
* https://github.com/peterbrittain/asciimatics

some example videos are here:
* https://www.youtube.com/watch?v=DpbKHvXaTRo
* https://youtu.be/5Qfv_jGQHBA

# Quick Start
* download/clone the repository
* install the dependancies.  The main ones are asciimatics, pythonosc and argsparse 
* open a terminal and type `python3 ASCII-Simple-Video-Synth.py` .  This will start the program in the default state.
* open a second terminal and type `python3 osc-sender.py` .  This will start sending randomly generated OSC control messages to the drawing process

# Drawing performance
Make sure you have the latest Asciimatics library.  (currently v1.11)  There was a big performance increase after v1.9

# OSC Control
As the system is inspired by 8-bit computers etc, paramater ranges are 0-255, except for mode which is 0-7

`<colours>` = red, green or blue

the synth responds to OSC commands at:
* `/<colour>/speed`
* `/<colour>/mode`
* `/<colour>/offset`
* `/<colour>/scale`

The shape drawing paramaters are:
* `/shape/sides` - The number of sides the shape has.
* `/shape/size` - The size of the shape.
* `/shape/xinc` - the rate of increment for the x value.
* `/shape/yinc` -  the rate of increment for the y value.

There is a TouchOSC control interface.
it looks like 
![TouchOSC Interface](https://github.com/zarquin/ASCII-Simple-Video-Synth/blob/master/TouchOSC-Interface.jpeg?raw=true)

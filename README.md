# ASCII-Simple-Video-Synth
A simple video synth for Consoles, controlled by OSC

some example videos are here:
* https://www.youtube.com/watch?v=DpbKHvXaTRo
* https://youtu.be/5Qfv_jGQHBA

# Quick Start
* download/clone the repository
* install the dependancies.  The main ones are asciimatics, pythonosc and argsparse 
* open a terminal and type `python3 ASCII-Simple-Video-Synth.py` .  This will start the program in the default state.
* open a second terminal and type `python3 osc-sender.py` .  This will start sending randomly generated OSC control messages to the drawing process


# OSC Control
`<colours>` = red, green or blue

the synth responds to OSC commands at:
* `/<colour>/speed`
* `/<colour>/mode`
* `/<colour>/offset`
* `/<colour>/scale`


There is a TouchOSC control interface.
it looks like 
![TouchOSC Interface](https://github.com/zarquin/ASCII-Simple-Video-Synth/blob/master/TouchOSC-Interface.jpeg?raw=true)

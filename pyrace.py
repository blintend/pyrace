#! /usr/bin/env python

# TODO:
#
# score line; score for time
# high score
# fuel; fuel pickup
# config file
# nice splash, Game Over
# slippery oil
# colors
# reliable speed (even if key pressed)

import curses
import random

TICK = 2
CAR = "^"
ROAD = " "
OBS = "X"
EDGE = "||"
RWIDTH = 8
RSLICE = EDGE + ROAD*RWIDTH + EDGE
LEFT_PROB = 0.4
RIGHT_PROB = LEFT_PROB
LR_PROB = LEFT_PROB + RIGHT_PROB
OBS_PROB = 0.2
ESC = 27

def init(win):
    curses.halfdelay(TICK)
    curses.curs_set(0)
    win.scrollok(1)
    

def main(win):
    
    init(win)
    (he, wi) = win.getmaxyx()
    cary = he-1
    carx = wi/2
    rx_max = (wi-len(RSLICE))
    rx = rx_max/2
    
    for i in range(0, he):
        win.addstr(i, rx, RSLICE)
        
    crash = 0
    esc = 0
    while not crash:
        ch = win.getch()
        if ch==curses.KEY_LEFT and carx>0:
            carx -= 1
        elif ch==curses.KEY_RIGHT and carx<wi-1:
            carx+=1
        elif ch==ESC:
            esc=1
            break
            
        r = random.random()
        if r<LR_PROB:
            if r<LEFT_PROB and rx>0:
                rx -= 1
            elif r>=LEFT_PROB and rx<rx_max:
                rx +=1

        r = random.random()
        if r<OBS_PROB:
            ox = int(RWIDTH*(r/OBS_PROB))
        else:
            ox = None

        win.scroll(-1)
        win.addstr(0, rx, RSLICE)
        if ox!=None:
            win.addstr(0, rx+len(EDGE)+ox, OBS)
        crash = win.inch(cary, carx)!=ord(ROAD)
        win.addstr(cary, carx, CAR)
        

curses.wrapper(main)

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
# gas, break (or link break to steering)

import curses
import random

TICK = 1
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

class Race:

    def __init__(self, race_win):
        self.race_win = race_win
        self.race_win.scrollok(1)
        (self.height, self.width) = race_win.getmaxyx()
        self.cary = self.height-1
        self.carx = self.width/2
        self.rx_max = (self.width-len(RSLICE))
        self.rx = self.rx_max/2
        self.ox = None
        for i in range(self.height):
            self.race_win.addstr(i, self.rx, RSLICE)
        self.crash = 0
        self.esc = 0

    def main_loop(self):
        while not self.crash and not self.esc:
            self.key(self.race_win.getch())
            self.next_rslice()
            self.next_obs()
            self.update_screen()

    def key(self, ch):
        if ch==curses.KEY_LEFT and self.carx>0:
            self.carx -= 1
        elif ch==curses.KEY_RIGHT and self.carx<self.width-1:
            self.carx += 1
        elif ch==ESC:
            self.esc=1

    def next_rslice(self):
        r = random.random()
        if r<LR_PROB:
            if r<LEFT_PROB and self.rx>0:
                self.rx -= 1
            elif r>=LEFT_PROB and self.rx<self.rx_max:
                self.rx +=1

    def next_obs(self):
        r = random.random()
        if r<OBS_PROB:
            self.ox = int(RWIDTH*(r/OBS_PROB))
        else:
            self.ox = None

    def update_screen(self):
        self.race_win.scroll(-1)
        self.race_win.addstr(0, self.rx, RSLICE)
        if self.ox!=None:
            self.race_win.addstr(0, self.rx+len(EDGE)+self.ox, OBS)
        self.crash = self.race_win.inch(self.cary, self.carx)!=ord(ROAD)
        self.race_win.addstr(self.cary, self.carx, CAR)
        
class Game:

    def __init__(self, main_win):
        self.main_win = main_win
        self.race = Race(main_win)

    def main_loop(self):
        self.race.main_loop()


def main(win):
    curses.halfdelay(TICK)
    curses.curs_set(0)
    game = Game(win)
    game.main_loop()
        

curses.wrapper(main)

#! /usr/bin/env python

# TODO:
#
# reliable speed (even if key pressed)
# high score; nice status line
# fuel; fuel pickup
# config file
# nice splash, Game Over
# slippery oil
# colors
# gas, break (or link break to steering)
# high score table

import curses
import random
import string

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

    def __init__(self, main_win):
        self.race_win = main_win.derwin(1, 0)
        self.race_win.keypad(1)
        self.race_win.scrollok(1)
        (self.height, self.width) = self.race_win.getmaxyx()
        self.status_line = StatusLine(main_win.derwin(1, self.width, 0, 0))
        self.score = 0
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
            self.score += 1
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
        self.status_line.update_score(self.score)
        self.status_line.refresh()

class StatusLine:

    SCORE_LABEL = "Score: "
    SCORE_WIDTH = 5
    
    def __init__(self, status_win):
        self.status_win = status_win
        self.width = status_win.getmaxyx()[1]
        self.score_pos = self.width-StatusLine.SCORE_WIDTH-1
        self.status_win.addstr(0, self.score_pos-len(StatusLine.SCORE_LABEL),
                               StatusLine.SCORE_LABEL)
        
    def update_score(self, score):
        self.status_win.addstr(0, self.score_pos,
                               string.zfill(score, StatusLine.SCORE_WIDTH))

    def refresh(self):
        self.status_win.refresh()
        
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

#! /usr/bin/env python

# TODO:
#
# high score; nice status line
# fuel; fuel pickup
# config file
# nice splash, Game Over
# slippery oil
# colors
# gas, break (or link break to steering)
# high score table
# pause key

import curses
import random
import string
import time
import math

TICK = 0.15
CAR = "^"
ROAD = " "
BONUS = "*"
OBS = "="
OIL = "Q"
EDGE = "[]"
RWIDTH = 8
RSLICE = EDGE + ROAD*RWIDTH + EDGE
LEFT_PROB = 0.4
RIGHT_PROB = LEFT_PROB
LR_PROB = LEFT_PROB + RIGHT_PROB
BONUS_PROB = 0.05
OBS_PROB = 0.2
OIL_PROB = 0.2
OIL_DUR = 4
SCORE_TICK = 1
SCORE_BONUS = 100
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
        self.bx = None
        self.ox = None
        self.oilx = None
        self.slip = 0
        for i in range(self.height):
            self.race_win.addstr(i, self.rx, RSLICE)
        self.crash = 0
        self.esc = 0
        self.event_loop = EventLoop(self.race_win, TICK,
                                    self.tick, self.key, self.is_quit)

    def run(self):
        self.event_loop.run()

    def is_quit(self):
        return self.crash or self.esc

    def tick(self):
        self.score += SCORE_TICK
        if self.slip>0: self.slip -= 1
        self.next_rslice()
        self.next_bonus()
        self.next_obs()
        self.next_oil()
        self.update_screen()

    def key(self, ch):
        delta = 0
        if ch==curses.KEY_LEFT and self.carx>0 and self.slip<=0:
            delta = -1
        elif ch==curses.KEY_RIGHT and self.carx<self.width-1 and self.slip<=0:
            delta = 1
        elif ch==ESC:
            self.esc=1
        self.carx += delta
        self.update_car(delta)

    def next_rslice(self):
        r = random.random()
        if r<LR_PROB:
            if r<LEFT_PROB and self.rx>0:
                self.rx -= 1
            elif r>=LEFT_PROB and self.rx<self.rx_max:
                self.rx +=1

    def next_bonus(self):
        r = random.random()
        if r<BONUS_PROB:
            self.bx = int(RWIDTH*(r/BONUS_PROB))
        else:
            self.bx = None

    def next_obs(self):
        r = random.random()
        if r<OBS_PROB:
            self.ox = int(RWIDTH*(r/OBS_PROB))
        else:
            self.ox = None

    def next_oil(self):
        r = random.random()
        if r<OIL_PROB:
            self.oilx = int(RWIDTH*(r/OIL_PROB))
        else:
            self.oilx = None

    def update_screen(self):
        self.race_win.scroll(-1)
        self.race_win.addstr(0, self.rx, RSLICE)
        self.update_car(0)
        self.status_line.set_score(self.score)
        self.status_line.noutrefresh()
        self.race_win.noutrefresh()
        curses.doupdate()

    def update_car(self, delta):
        if self.bx!=None:
            self.race_win.addstr(0, self.rx+len(EDGE)+self.bx, BONUS)
        if self.ox!=None:
            self.race_win.addstr(0, self.rx+len(EDGE)+self.ox, OBS)
        if self.oilx!=None:
            self.race_win.addstr(0, self.rx+len(EDGE)+self.oilx, OIL)
        c = self.race_win.inch(self.cary, self.carx)
        if c==ord(BONUS):
            self.score += SCORE_BONUS
        self.crash = c not in (ord(ROAD), ord(BONUS), ord(OIL), ord(CAR))
        if c==ord(OIL):
            self.slip += OIL_DUR
        if delta!=0: self.race_win.addstr(self.cary, self.carx-delta, ROAD)
        self.race_win.addstr(self.cary, self.carx, CAR)
        
class StatusLine:

    SCORE_LABEL = "Score: "
    SCORE_WIDTH = 5
    
    def __init__(self, status_win, score=0):
        self.status_win = status_win
        self.width = status_win.getmaxyx()[1]
        self.score_pos = self.width-StatusLine.SCORE_WIDTH-1
        self.status_win.addstr(0, self.score_pos-len(StatusLine.SCORE_LABEL),
                               StatusLine.SCORE_LABEL)
        self.score = score

    def set_score(self, score):
        self.score = score
        
    def noutrefresh(self):
        self.status_win.addstr(0, self.score_pos,
                               string.zfill(self.score,
                                            StatusLine.SCORE_WIDTH))
        self.status_win.noutrefresh()

class EventLoop:

    def __init__(self, win, tick, tick_func, key_func, quit_func):
        self.win = win
        self.tick = tick
        self.tick_func = tick_func
        self.key_func = key_func
        self.quit_func = quit_func
        self.next_tick = time.time()
        
    def run(self):
        while not self.quit_func():
            now = time.time()
            still = self.next_tick-now
            if still<=0:
                self.tick_func()
                self.next_tick += self.tick
            else:
                self.win.timeout(1000*still)
                ch = self.win.getch()
                if ch != curses.ERR:
                    self.key_func(ch)
            
class Game:

    def __init__(self, main_win):
        curses.curs_set(0)
        self.main_win = main_win
        self.race = Race(main_win)

    def run(self):
        self.race.run()


def main(win):
    game = Game(win)
    game.run()
        

curses.wrapper(main)

#! /usr/bin/env python

# TODO:
#
# high score; nice status line
# fuel; fuel pickup
# config file
# gas, break (or link break to steering)
# high score table
# pause key

import curses
import random
import string
import time

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
ENTER = 10

class Race:

    def __init__(self, main_win):
        self.main_win = main_win
        self.race_win = main_win.derwin(1, 0)
        self.race_win.keypad(1)
        self.race_win.scrollok(1)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
        Race.FIELD_PAIR = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
        Race.ROAD_PAIR = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        Race.BONUS_PAIR = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLUE)
        Race.OBS_PAIR = curses.color_pair(4)
        Race.OIL_PAIR = curses.color_pair(3)
        Race.CAR_PAIR = curses.color_pair(3)
        self.race_win.bkgdset(" ", curses.color_pair(1))
        (self.height, self.width) = self.race_win.getmaxyx()
        self.status_line = StatusLineView(main_win.derwin(1, self.width, 0, 0))
        self.rx_max = (self.width-len(RSLICE))
        self.event_loop = EventLoop(self.race_win, TICK,
                                    self.tick, self.key, self.is_quit)
        self.reset()
        
    def reset(self):
        self.race_win.erase()
        self.score = 0
        self.cary = self.height-1
        self.carx = self.width/2
        self.rx = self.rx_max/2
        self.bx = None
        self.ox = None
        self.oilx = None
        self.slip = 0
        for i in range(self.height):
            self.race_win.addstr(i, self.rx, RSLICE, Race.ROAD_PAIR)
        self.crash = 0
        self.esc = 0
        
    def run(self):
        self.reset()
        self.main_win.touchwin()
        self.main_win.refresh()
        self.event_loop.run()

    def is_quit(self):
        return self.crash or self.esc

    def is_esc(self):
        return self.esc
    
    def get_score(self):
        return self.score
    
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
        self.race_win.addstr(0, self.rx, RSLICE, Race.ROAD_PAIR)
        self.update_car(0)
        self.status_line.noutrefresh(self.score)
        self.race_win.noutrefresh()
        curses.doupdate()

    def update_car(self, delta):
        if self.bx!=None:
            self.race_win.addstr(0, self.rx+len(EDGE)+self.bx,
                                 BONUS, Race.BONUS_PAIR)
        if self.ox!=None:
            self.race_win.addstr(0, self.rx+len(EDGE)+self.ox,
                                 OBS, Race.OBS_PAIR)
        if self.oilx!=None:
            self.race_win.addstr(0, self.rx+len(EDGE)+self.oilx,
                                 OIL, Race.OIL_PAIR)
        c = self.race_win.inch(self.cary, self.carx) & 255
        if c==ord(BONUS):
            self.score += SCORE_BONUS
        self.crash = c not in (ord(ROAD), ord(BONUS), ord(OIL), ord(CAR))
        if c==ord(OIL):
            self.slip += OIL_DUR
        if delta!=0: self.race_win.addstr(self.cary, self.carx-delta, ROAD,
                                          Race.ROAD_PAIR)
        self.race_win.addstr(self.cary, self.carx,
                             CAR, Race.CAR_PAIR)
        
class StatusLineView:

    SCORE_LABEL = "Score: "
    SCORE_WIDTH = 5
    
    def __init__(self, status_win):
        self.status_win = status_win
        self.width = status_win.getmaxyx()[1]
        self.score_pos = self.width-StatusLineView.SCORE_WIDTH-1
        self.status_win.addstr(0, self.score_pos-len(StatusLineView.SCORE_LABEL),
                               StatusLineView.SCORE_LABEL)

    def noutrefresh(self, score):
        self.status_win.addstr(0, self.score_pos,
                               string.zfill(score, StatusLineView.SCORE_WIDTH))
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
                self.win.timeout(int(1000*still))
                ch = self.win.getch()
                if ch != curses.ERR:
                    self.key_func(ch)

class MainMenu:

    def __init__(self, main_win):
        self.menu_win = curses.newwin(main_win.getmaxyx()[0],
                                      main_win.getmaxyx()[1],
                                      main_win.getbegyx()[0],
                                      main_win.getbegyx()[1])
        self.menu_win.keypad(1)
        self.menu_win.box()
        addcenter(self.menu_win, 2, "PYRACE")
        addcenter(self.menu_win, 4, "Press any key to start")

    def activate(self):
        self.menu_win.touchwin()
        self.menu_win.refresh()
        return self.menu_win.getch()!=ESC
        
class GameOver:

    def __init__(self, race):
        main_win = race.main_win
        self.race = race
        [my, mx], [y0, x0] = main_win.getmaxyx(), main_win.getbegyx()
        self.over_win = curses.newwin(my/2, mx/2, y0 + my/4, x0 + mx/4)
        self.over_win.keypad(1)
        self.over_win.box()
        addcenter(self.over_win, 2, "GAME OVER")
        self.over_win.addstr(4, 1, "Score:")
        addcenter(self.over_win, 6, "Press Enter to continue")

    def activate(self):
        self.over_win.addstr(4, 8, string.zfill(self.race.get_score(), 5))
        self.over_win.touchwin()
        self.over_win.refresh()
        key = self.over_win.getch()
        while not key in (ENTER, ESC):
            key = self.over_win.getch()
        return key!=ESC

class Game:

    def __init__(self, main_win):
        curses.curs_set(0)
        self.main_win = main_win
        self.race = Race(main_win)
        self.menu = MainMenu(main_win)
        self.over = GameOver(self.race)

    def run(self):
        while self.menu.activate():
            self.race.run()
            if not self.race.is_esc():
                cont = self.over.activate()
                if not cont: break

# Utilities

def addcenter(win, y, str): win.addstr(y, (win.getmaxyx()[1] - len(str)) / 2, str)

# main
def main(win):
    game = Game(win)
    game.run()
        

curses.wrapper(main)

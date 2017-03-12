#!/usr/bin/env python3.6

class Map(object):

    def __init__(self, bounds):
        self.grid = { (y,x):{} for y in range(bounds[0]) for x in range(bounds[1]) }

class MapTile(object):

    def __init__(self, pos):
        self.items = {}
        self.items['character'] = ' '           # Default to blank space
        self.items['mode'] = curses.A_NORMAL    # Default to normal output mode

class MapGenerator(object):

    def __init__(self, dimy, dimx):
        self.map = {}
        self.next_map = 0
        self.bounds = dimy, dimx

    def add_map(self):
        retval = Map(self.bounds)
        self.map[self.next_map] = retval
        self.next_map += 1
        return retval

    def get_map(self, level):
        if level in self.map:
            return self.map[level]
        elif level == self.next_map:
            self.add_map()
            return self.map[level]

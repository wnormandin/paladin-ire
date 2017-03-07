#!/usr/bin/env python2.7
#-*- coding: utf-8 -*i-

from .core import Entity

class Player(Entity):
    """ Player class containing all methods and properties """

    def __init__(self):
        self.score = 0
        self.initialized = False    # Set to true after CharCreate()
        super(Player, self).__init__()

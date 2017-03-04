#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import logging

from scripts.player_creation import character_creation
from player.player import Player

if __name__ == '__main__':
    character_creation(Player())

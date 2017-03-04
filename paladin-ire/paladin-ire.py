#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import logging
from scripts.player_creation import character_creation
from player.player import Player

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--create',action='store_true',help='Create a new character')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.create:
        p = Player()
        character_creation(p)

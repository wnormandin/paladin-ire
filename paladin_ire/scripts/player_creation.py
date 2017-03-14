#!/usr/bin/env/python2.7
#-*- coding: utf-8 -*-

#   Main Menu
#   Using ../player/*, generate a player
#   Menu-Driven, optionally run as a
#   command-line script with options to
#   create PC/NPC templates

# stdlib modules
import curses

# package
from game.menu import Menu, MenuItem, AttributeSelection, ClassSelection, OptionMenu
from game.core import MapWindow
from game.color import color_wrap, Color
from game.player import Player
from .world_generation import MapGenerator

class MainMenu(object):

    def __init__(self, stdscreen, player, parent):
        self.parent = parent
        self.args = parent.args
        self.screen = stdscreen
        self.player = player
        self.map_generator = None
        self.menu_items=(
                MenuItem('New Player', self.recreate_player, 0),
                MenuItem('Select Class', self.class_select, 1),
                MenuItem('Set Attributes', self.attr_select, 2),
                MenuItem('Start Game', self.go, 3),
                MenuItem('Options', self.opt_menu, 4)
                )
        self.populate_menu()
        self.main_menu.display()

    def recreate_player(self):
        self.parent.player = self.player = Player()
        self.main_menu.msg_bar('[*] Player refreshed')
        self.main_menu.draw_charinfo()

    def go(self):
        game = MapWindow(self.screen, self.parent)
        # game.post_init()
        return game.display()

    def opt_menu(self):
        menu = OptionMenu(self.screen, self)
        menu.post_init()
        return menu.display()

    def class_select(self):
        menu = ClassSelection(self.screen, self)
        menu.post_init()
        return menu.display()

    def attr_select(self):
        if self.player.player_class is None:
            self.main_menu.current_msg = 'Select a Class first!'
            self.main_menu.msg_bar()
            return
        menu = AttributeSelection(self.screen, self)
        menu.post_init()
        return menu.display()

    def populate_menu(self):
        item_list = []
        for item in self.menu_items:
            item_list.append(item)
        self.main_menu = Menu(self.screen, self)
        self.main_menu.post_init(item_list)

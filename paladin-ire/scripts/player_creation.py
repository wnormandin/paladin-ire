#!/usr/bin/env/python2.7
#-*- coding: utf-8 -*-

#   PC/NPC Generation Script
#   Using ../player/*, generate a player
#   Menu-Driven, optionally run as a
#   command-line script with options to
#   create PC/NPC templates

# stdlib modules
import curses

# package
from util.menu import Menu, MenuItem, AttributeSelection, ClassSelection, OptionMenu
from util.color import color_wrap, Color

class CharCreate(object):

    def __init__(self, stdscreen, player, args):
        self.args = args
        self.screen = stdscreen
        self.curses_init()
        self.player = player

        self.menu_items=(
                MenuItem('Select Class', self.class_select, 0),
                MenuItem('Set Attributes', self.attr_select, 1),
                MenuItem('Start Game', self.go, 2),
                MenuItem('Options', self.opt_menu, 3)
                )

        self.populate_menu()
        self.main_menu.display()

    def go(self):
        # no-op
        pass

    def opt_menu(self):
        menu = OptionMenu(self.screen, self)
        menu.post_init()
        return menu.display()

    def curses_init(self):
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        self.set_colors()

    def set_colors(self):
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)

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

def character_creation(player, args):
    curses.wrapper(CharCreate, player, args)

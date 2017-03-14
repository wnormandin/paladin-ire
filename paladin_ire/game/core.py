#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

# Parent classes for most game objects
# Curses menu and game window superclasses

import curses
import random
from curses import panel

from scripts.world_generation import MapGenerator

NAME_LIST=['Flargin', 'Dingo', 'Mypaltr', 'Pallyride', 'Pallindrome', 'Jeff', 'Chaz',
           'Molly', 'Martin', 'Grena', 'Palson', 'Rempo', 'Trixy', 'Mouse', 'Pal']

class RandomRoll(object):

    """ Random Roller, instantiated by the main game app and used for all checks """

    DISADV = -1
    ZERO = 0
    ADV = 1
    CRIT = 2

    def __init__(self,player,ubound,lbound=1):
        self.player = player
        self.ub = ubound    # Random roll range upper-bound
        self.lb = lbound    # Random roll range lower-bound

    def _calc_adv(self, skill):
        # Calculates skill checks
        if skill is not None:
            chk_mod = getattr(self.player, skill)
            return (chk_mod / self.player.attr_limit) + 1.
        return 2.

    @property
    def possibles(self):
        return list(range(self.min_val, self.max_val))

    def calc_bound(self,bound,mult=1.):
        assert isinstance(mult, float)
        return int(bound * mult)

    def execute(self):
        return random.choice(self.possibles)

    def attr_roll(self, attr):
        return self._calc_adv(attr)

    def roll(self,check,init=False):
        self.max_val = self.calc_bound(self.ub, max(2., self.attr_roll(check)))
        if not init:
            self.min_val = self.calc_bound(self.lb, self.attr_roll('luck'))
        else:
            self.min_val = 1
        return self.execute()

    def resist_roll(self, resist):
        adv = self._calc_adv(resist)
        max_val = self.skill_max_val()
        result = self.roll(resist)
        return abs((result/max_val) - adv)

    def atk_roll(self, goal):
        # goal = roll attr or save for target/enemy
        result = self.roll('attack')
        if (result/float(goal)) > 1.25:
            return self.CRIT
        elif result >= goal:
            return self.ADV
        elif result == 0:
            return self.ZERO
        elif result < goal:
            return self.DISADV

class Entity(object):

    """ General attributes/properties/methods for PC/NPC Entities """

    attributes = ["health", "attack", "defense", "focus", "strength", "wisdom", "luck"], 1
    resists = ["fire", "frost", "death", "detection"], 0
    status_effects = ["blind", "paralyzed", "invincible", "fast"], 0
    player_stats = {
                    'hitpoints':(['health', 'health', 'defense'], False),
                    'magic':(['wisdom', 'wisdom', 'focus'], False),
                    'evade':(['defense', 'focus'], False),
                    'carry':(['strength', 'strength', 'health'], False),
                    'dodge':(['defense'], True),
                    'sneak':(['focus'], True),
                    'kick':(['strength'], True),
                    'bash':(['strength'], True),
                    'alteration':(['wisdom'], True),
                    'destruction':(['wisdom'], True),
                    'conjuration':(['wisdom'], True),
                    'block':(['strength'], True),
                    'backstab':(['focus'], True),
                    'max_damage':(['strength', 'attack', 'luck'], True)
                   }
    core_stats = ['carry', 'hitpoints', 'magic', 'evade', 'max_damage']

    attr_desc = {
                 'health':'Contributes to\nplayer hit points',
                 'attack':'Affects damage\ndealt by the\nplayer',
                 'defense':'Contributes to\ndamage mitigation\nand dodging',
                 'focus':'Affects ranged\ndamage, spell\ncasting, and\nhit likelihood',
                 'strength':'Contributes to\ndamage and\ncarry capacity',
                 'wisdom':'Determines spell\ndamage and\nmana',
                 'luck':'Increases critical\nhit potential\nand save roll\nbaselines'
                }

    def __init__(self):
        self.alive = True
        self._attr_init()
        self.level = 1
        self.player_class = None
        self.init_complete = False
        self.damage = 0
        self._skills_enabled = None
        self.name = ''
        self.max_hp = 1
        self.max_mp = 1
        self.hitpoints = 0
        self.magic = 0

    @property
    def sneaks(self):
        cls = self.player_class
        if cls is None or not cls.sneak_enable:
            return False
        elif cls.sneak_enable:
            return True

    @property
    def spells(self):
        cls = self.player_class
        if cls is None or not cls.spell_book_enable:
            return False
        elif cls.spell_book_enable:
            return True

    def _attr_init(self):
        attrs = self.attributes, self.resists, self.status_effects
        for group in attrs:
            items, default = group
            for item in items:
                setattr(self, item, default)

    def complete_init(self):
        # Magic and hitpoints need to persist and not
        # calculate during gameplay
        self.hitpoints = self.get_stat('hitpoints')
        self.magic = self.get_stat('magic')
        self.max_hp = self.hitpoints
        self.max_mp = self.magic
        self.init_complete = True

    def heal(self, pts=0):
        if pts == 0:
            self.hitpoints = self.max_hp
        else:
            self.hitpoints = min( self.max_hp, self.hitpoints + pts )

    def get_stat(self, stat):
        if stat not in self._skills_enabled:
            return 1

        calc_stat, lvl_based = self.player_stats[stat]
        stat_val = sum([getattr(self, s) for s in calc_stat])
        if not lvl_based:
            return int((stat_val / float(self.attr_limit))*10 + stat_val)
        else:
            return self.level + stat_val

    @property
    def _skills_enabled(self):
        base = self.core_stats
        if self.player_class is not None:
            base.extend(self.player_class.class_skills)
        for sk in ['sneaks', 'spells']:
            if getattr(self, sk):
                base.append(sk)
        return base

    @_skills_enabled.setter
    def _skills_enabled(self,skill=None):
        cls = self.player_class
        if cls is None:
            return
        if skill is None:
            if cls.spell_book_enable and not self.spells:
                self.spells = True
            if cls.sneak_enable and not self.sneaks:
                self.sneaks = True
        else:
            setattr(self, skill, True)

    @property
    def attr_sum(self):
        # Calculate the entity's currently used attribute points
        return sum([getattr(self, a) for a in self.attributes[0]])

    @property
    def attr_limit(self):
        # Calculate the entity attribute point limit
        return (self.level * 10) + 15

    @property
    def free_attr(self):
        # Return the number of attribute points not assigned
        return self.attr_limit - self.attr_sum

    def pre_turn(self):
        """ Pre-Turn hook, status effects decremented """
        effects, _ = self.status_effects
        for eff in effects:
            val = getattr(self, eff)
            if val > 0:
                val -= 1
                setattr(self, eff, val)

    @property
    def alive(self):
        if self.hitpoints > 0: return True
        return False

    @alive.setter
    def alive(self, revive):
        # Allows reviving/killing a player by setting
        # the alive property to True/False
        if revive: self.hitpoints = 1
        else: self.hitpoints = 0

    @property
    def hp_percent(self):
        return self.hitpoints / self.max_hp

    @property
    def mp_percent(self):
        return self.magic / self.max_mp


class GameWindow(object):
    def __init__(self, stdscreen, app):
        self.stdscreen = stdscreen
        self.window = stdscreen.subwin(0, 0)
        self.set_styles()
        self.window.keypad(1)
        self._panel_init()
        self.maxy, self.maxx = self.window.getmaxyx()
        self.app = app
        self.dbg_msg_list = []
        self.current_msg = ''
        self.over = None
        self.last_keystroke = None
        self.start_pos = 0
        self._init_windows()

    def _panel_init(self):
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

    def _init_windows(self):
        self.char_win, self.char_panel = self.side_panel(6, 29,
                                                         self.maxy - 8, 2)
        self.moves_win, self.moves_panel = self.side_panel(6, 45,
                                                           self.maxy - 8, 31)
        self.tile_win, self.tile_panel = self.side_panel(10, 25,
                                                         2, self.maxx - 27)

    def _refresh_subwindows(self):
        self.draw_charinfo()
        self.draw_moves()
        self.draw_tileinfo()

    def _overlay_subwindows(self):
        for win in self.char_win, self.moves_win, self.tile_win:
            win.overlay(self.window)

    def draw_tileinfo(self):
        self.tile_win.box()

    def draw_moves(self):

        def draw_arrows():
            self.moves_win.addstr(1, 2, 'Moves', curses.A_UNDERLINE)
            for ch in upch, dnch, lch, rch:
                self.moves_win.addch(*ch)

        for i in range(1,5):
            self.moves_win.move(i,2)
            self.moves_win.clrtoeol()

        default_mode = curses.A_DIM
        upch = 2, 4, curses.ACS_UARROW, default_mode
        dnch = 4, 4, curses.ACS_DARROW, default_mode
        lch = 3, 3, curses.ACS_LARROW, default_mode
        rch = 3, 5, curses.ACS_RARROW, default_mode
        draw_arrows()

        self.moves_win.box()

    def draw_charinfo(self):
        win = self.char_win

        for i in range(1, 5):
            win.move(i, 2)
            win.clrtoeol()

        # Display player name
        win.addstr(1, 2, 'Player :  {:>15}'.format(self.app.player.name))

        # Display player class
        cls = self.app.player.player_class
        cls_str = 'None' if cls is None else cls.__class__.__name__
        win.addstr(2, 2, 'Class  :  {:>15}'.format(cls_str))

        # Display health indicator
        hp_str = '*' * int(((self.app.player.hp_percent * 100) + 9) // 10)
        win.addstr(3, 2, 'HP     :  ({:>2}) {:->10}'.format(
            self.app.player.hitpoints,
            hp_str
        ))

        # Display magic indicator
        mp_str = '*' * int(((self.app.player.mp_percent * 100) + 9) // 10)
        win.addstr(4, 2, 'MP     :  ({:>2}) {:->10}'.format(
            self.app.player.magic,
            mp_str
        ))

        win.box()

    def execute(self):
        while True:
            self._loop_begin()
            self._overlay_subwindows()
            self._refresh_subwindows()
            if not self.main_loop():
                break
            self._loop_end()

    def main_loop(self):
        input('continue')
        return False

    def msg_bar_prompt(self, prompt, default=None):
        # displays the prompt in the message bar and
        # awaits user input, 15 characters max. A
        # default value should be specified and in
        # the prompt via format spec
        self.msg_bar(prompt.format(default))
        msg_len = len(self.current_msg)
        entry = self.capture(self.maxy - 2, msg_len + 1, 15)
        if not entry:
            entry = default
        return entry

    def display(self):
        self._pre_loop()
        self.execute()
        self._post_loop()
        return self.current_msg

    def clear_win(self, win):
        for j in range(win.getmaxyx()[0]):
            self._pre_draw(j, 1)

    def side_panel(self, h, l, y, x):
        win = curses.newwin(h, l, y, x)
        # win.erase()
        win.box()
        panel = curses.panel.new_panel(win)
        return win, panel

    def set_styles(self):
        self.info_msg = curses.color_pair(1)
        self.err_msg = curses.color_pair(2)
        self.hlt_msg = curses.color_pair(3)
        self.margin = 3

    def menu_bar(self, val_list=('S: Save', 'Q: Quit')):
        if val_list:
            menu = ' | '.join(val_list)
            self._pre_draw(1, 2)
            self.window.addstr(1, 2, menu, curses.color_pair(3))

    def msg_bar(self, msg=None):
        if msg is not None: self.current_msg = msg
        if self.current_msg is None: self.current_msg = ''
        yval, xval = self.window.getmaxyx()
        col = self.hlt_msg
        self.window.addstr(
            yval - 2,
            2,
            self.current_msg.ljust(xval - 2),
            col
        )

    def _loop_begin(self):
        self.window.noutrefresh()
        self.window.box()
        curses.doupdate()

    def _loop_end(self):
        # Draw debug info, the top menu  bar, and the bottom msg bar
        # at the end of each main_loop iteration
        self.debug_info()
        self.menu_bar()
        self.msg_bar()

    def _pre_draw(self, yv, xv):
        win = self.window
        win.move(yv, xv)
        win.clrtoeol()
        win.noutrefresh()

    def capture(self, y, x, length):
        # Capture user input for <length> chars at (y,x)
        curses.echo()
        self.window.move(y, x)
        val = self.window.getstr(y, x, length)
        curses.noecho()
        self.window.move(0, 0)
        return val.decode(encoding='utf-8')

    def debug_info(self):

        if self.app.args.debug or self.app.args.verbose:
            yval, xval = curses.getsyx()
            y = self.maxy - 6
            x = self.maxx - 17

            col = self.info_msg
            self.msg_list = [
                'pos:{}'.format(self.position),
                'over:{}'.format(self.over),
                'maxy:{}'.format(self.maxy),
                'maxx:{}'.format(self.maxx),
                'cursor:{},{}'.format(yval, xval),
                'key:{}'.format(self.last_keystroke)
            ]

            for i, val in enumerate(self.msg_list):
                self._pre_draw(y - i, x)
                self.window.addstr(y - i, x, val, col)

    def _parse_keystroke(self, key):
        if key in [curses.KEY_ENTER, ord('\n')]:
            return 'enter'
        elif key in [curses.KEY_BACKSPACE, ord('\b'), 127]:
            return 'backspace'
        elif key in [curses.KEY_UP, 65]:
            return 'up'
        elif key in [curses.KEY_DOWN, 66]:
            return 'down'
        elif key in [curses.KEY_LEFT, 68]:
            return 'left'
        elif key in [curses.KEY_RIGHT, 67]:
            return 'right'
        elif key in [' ', ord(' ')]:
            return 'space'
        elif key in [113, ord('q'), 81, ord('Q')]:
            return 'q'
        else:
            return r'{}'.format(key)


class MapWindow(GameWindow):
    def __init__(self, stdscreen, app):
        super().__init__(stdscreen, app)
        bounds = self.map_win_bounds()
        self.map_gen = MapGenerator(bounds[0] - 1, bounds[2] - 1)
        self.map_win, self.map_panel = self.side_panel(*bounds)
        self.current_level = self.map_gen.add_map()
        self.position = 0

    def map_win_bounds(self):
        self.maxy, self.maxx = self.window.getmaxyx()
        map_minx = 1
        map_maxx = 75
        map_miny = 1
        map_maxy = self.maxy - 8
        return map_maxy - map_miny, map_maxx - map_minx, 2, 2

    def draw_map(self):

        def _clear():
            wy, wx = self.map_win.getmaxyx()
            for i in range(1, wy):
                self.map_win.move(i, 1)
                self.map_win.clrtoeol()

        _clear()
        self.map_win.box()
        for y in range(1, self.map_gen.bounds[0]):
            for x in range(1, self.map_gen.bounds[1]):
                tile = self.current_level.grid[y, x]
                if not tile:
                    msg = ' '
                    mode = curses.A_NORMAL
                else:
                    msg = tile.char
                    mode = tile.mode
                self.map_win.addch(y, x, msg, mode)

    def main_loop(self):
        self.menu_bar(val_list=['Q: Main Menu'])
        self.draw_map()
        self._refresh_subwindows()
        self.msg_bar('Choose an action')
        return self.process_selection(self.map_win.getch())

    def process_selection(self, key):
        self.last_keystroke = self._parse_keystroke(key)
        if self.last_keystroke in ['enter']:
            # Open doors and other actions
            return True
        elif self.last_keystroke in ['esc', 'q']:
            # Exit to the menu
            return False
        elif self.last_keystroke in ['up', 'down', 'left', 'right']:
            # Move the player
            return True
        elif self.last_keystroke in ['space']:
            # Space to be used for picking up items
            return True

        self.draw_charinfo()
        return True

    def draw_entities(self):
        pass

    def _pre_loop(self):
        pass

    def _post_loop(self):
        pass
import curses
import json
from curses import panel
import random

from player.attributes import ATTRIBUTE_DESCRIPTIONS as attr_desc
from player.core import RandomRoll as roll
from player.core import NAME_LIST
from player.classes import CLASSES
import player.classes

class Menu(object):

    def __init__(self, stdscreen, app):
        self.window = stdscreen.subwin(0,0)
        self.set_styles()
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
        self.position = 0
        self.maxy,self.maxx = self.window.getmaxyx()
        self.app = app
        self.dbg_msg_list = []
        self.current_msg = ''
        self.first_pass = True
        self.over = None

    def menu_bar(self,val_list=['S: Save','Q: Quit']):
        if val_list:
            menu = ' | '.join(val_list)
            self._pre_draw(1,2)
            self.window.addstr(1,2,menu,curses.color_pair(3))

    def msg_bar(self,msg=' '):
        yval,xval = self.window.getmaxyx()
        col = self.hlt_msg
        self.window.addstr(
            yval-2,
            2,
            self.current_msg.ljust(xval-2),
            col
            )

    def draw_sidewin(self,title,msg):
        self._pre_draw(2,2)
        self.side_win.addstr(2,self.margin+1,title,
                curses.A_BOLD | curses.color_pair(3)
                )
        i = self.margin+1
        self.clear_sidewin()
        for line in msg.split('\n'):
            self.side_win.addstr(i,self.margin+1,line)
            i += 1

    def clear_sidewin(self):
        for j in range(self.side_win.getmaxyx()[0]):
            self._pre_draw(j,2)

    def side_panel(self, h, l, y, x):
        win = curses.newwin(h,l,y,x)
        win.erase()
        win.box()
        panel = curses.panel.new_panel(win)
        return win, panel

    def _pre_draw(self,yv,xv):
        self.window.move(yv,xv)
        self.window.clrtoeol()

    def debug_info(self):

        yval,xval = curses.getsyx()
        y = self.maxy-4
        x = self.maxx-17

        col = self.info_msg
        self.msg_list = [
                        'pos:{}'.format(self.position),
                        'over:{}'.format(self.over),
                        'maxy:{}'.format(self.maxy),
                        'maxx:{}'.format(self.maxx),
                        'cursor:{},{}'.format(yval,xval)
                        ]

        for i,val in enumerate(self.msg_list):
            self._pre_draw(y-i,x)
            self.window.addstr(y-i,x,val,col)

    def set_styles(self):
        self.info_msg = curses.color_pair(1)
        self.err_msg = curses.color_pair(2)
        self.hlt_msg = curses.color_pair(3)

        self.margin = 3

    def capture(self,y,x,length):
        curses.echo()
        self.window.move(y,x)
        val = self.window.getstr(y,x,length)
        curses.noecho()
        self.window.move(0,0)
        return val

    def post_init(self, items):
        self.items = items
        self.items.append(MenuItem('Back','exit',len(items)))

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) -1

    def _pre_loop(self):
        self.maxy, self.maxx = self.window.getmaxyx()
        self.panel.top()
        self.panel.show()
        self.window.clear()
        self.window.box()
        self.first_pass = True

    def display(self):
        self._pre_loop()
        self.main_loop()
        self._post_loop()
        return self.current_msg

    def _post_loop(self):
        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    def main_loop(self):
        while True:
            self.window.refresh()
            curses.doupdate()
            for item in self.items:
                if item.index == self.position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL

                self.window.addstr(2+item.index, 2, item.label, mode)

            if not self.first_pass:
                self.tmp_msg = self.current_msg
                key = self.window.getch()
            else:
                self.tmp_msg = None
                key = None
                self.first_pass = False

            if key in [curses.KEY_ENTER, ord('\n')]:
                if self.position == len(self.items)-1:
                    break
                else:
                    self.current_msg = self.items[self.position].hook()

            elif key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)

            if self.tmp_msg is not None:
                if self.position == len(self.items)-1:
                    self.current_msg = 'Press ENTER to exit'
                else:
                    self.current_msg = 'Press ENTER to select this option'

            self.msg_bar()

class MenuItem():

    def __init__(self, label, hook, index, args=None, pop=True, req=True):
        self.label = label
        self.hook = hook
        self.args = args
        self.pop = pop
        self.index = index
        self.req = req

class AttributeSelection(Menu):

    SELECT = 1  # Option selection mode
    EDIT = 2    # Attribute edit mode
    TEST = 3    # Unused at this time

    def attr_init(self):
        # rolls initial player attributes
        rr = roll(self.player, 7)
        attr_list = self.player.attributes[0]

        # Seed initial stats
        while True:
            for a in attr_list:
                result = rr.roll(None)
                setattr(self.player,a, result)
            if self.player.free_attr < 16 and self.player.free_attr > 10:
                break

        # Distribute remainder based on class
        cls = self.player.player_class
        preferred = [attr for attr in cls.preferred_attr]
        preferred.append('health')
        while self.player.free_attr > 5:
            a = random.choice(attr_list)
            if a in preferred:
                setattr(self.player, a, getattr(self.player, a)+1)

        # Set resists
        for resist in cls.resists:
            setattr(self.player,resist,cls.resists[resist])

        self.refresh_attributes()

    def post_init(self, player):
        self.player = player
        self.refresh_attributes()
        self.side_win, self.desc_panel = self.side_panel(12, 24, 2, 48)

    def refresh_attributes(self):
        attrs, _ = self.player.attributes
        self.items = [(attr, getattr(self.player,attr)) for attr in attrs]
        self.items.extend([('Re-roll',''),('Done','')])

    def _post_loop(self):
        self.window.clear()
        self.panel.hide()
        self.side_win.clear()
        self.desc_panel.hide()
        panel.update_panels()
        curses.doupdate()

    def _pre_loop(self):
        self.panel.top()
        self.panel.show()
        self.window.clear()
        self.window.box()

    def _draw_desc(self):
        self.desc_panel.top()
        self.desc_panel.show()
        self.side_win.clear()
        self.side_win.box()


    def _loop_start(self):
        self.window.refresh()
        self.window.box()
        self.side_win.overlay(self.window)
        self._draw_desc()
        curses.doupdate()

    def main_loop(self):
        assert self.player.player_class is not None
        self.position=8
        while True:
            # Loop init, refresh windows and print menus
            self._loop_start()
            # Print menu items
            self.print_item_list()
            # Print resist values
            self.print_resist_list()
            # Calculate and print player stats
            self.print_player_stats()
            # Print the menu bar (Save/Quit)
            self.menu_bar()

            if not self.first_pass:
                if not self.process_selection(self.window.getch()):
                    break
            else:
                self.attr_init()

            self.first_pass = False

            self.debug_info()
            self.msg_bar()

    def process_selection(self,key):
        if key in [curses.KEY_ENTER, ord('\n')]:
            if self.position == len(self.items)-1:
                self.over=None
                return False
            elif self.position == len(self.items)-2:
                self.over = 're-roll'
                self.player._attr_init()
                self.attr_init()
                self.print_item_list()
                self.current_msg = 'Attributes re-rolled'
                self.msg_bar()
                return True
            else:
                if self.player.free_attr > 0:
                    self.incr_attr()
                else:
                    self.current_msg = 'No remaining attribute points'
                    self.msg_bar()
                    return True

        elif key == curses.KEY_UP:
            self.navigate(-1)

        elif key == curses.KEY_DOWN:
            self.navigate(1)

        elif key in [ord('S'),ord('s')]:
            return self.save_entity()

        elif key in [ord('Q'),ord('q')]:
            self.over=None
            return False

        if self.position < len(self.items)-2:
            self.over = self.player.attributes[0][self.position]
            self.attribute_info()
            self.current_msg = 'Hit ENTER to increase this attribute'
        elif self.position == len(self.items)-2:
            self.clear_sidewin()
            self.over = 're-roll'
            self.current_msg = 'Hit ENTER to re-roll attributes'
        else:
            self.clear_sidewin()
            self.over = 'done'
            self.current_msg = 'Hit ENTER to return to the previous menu'

        return True

    def incr_attr(self):
        self.debug_info()
        for idx, item in enumerate(self.items):
            if idx == self.position:
                setattr(self.player, item[0], int(getattr(self.player,item[0])+1))
                self.current_msg = 'Attribute: {}, new value: {}'.format(
                            item[0],
                            getattr(self.player,item[0])
                            )
                self.msg_bar()
        self.refresh_attributes()

    @property
    def getfilename(self):
        return random.choice(NAME_LIST)

    def save_entity(self):
        default = self.getfilename
        self.current_msg = 'Input a file name (Blank={}, 15 chars max): '.format(default)
        self.msg_bar()
        msg_len = len(self.current_msg)
        entry=self.capture(self.maxy-2,msg_len+1,15)
        if not entry:
            entry = default
        fname='./entities/{}'.format(entry)
        self.current_msg = 'Save entity "{}"? (Y/n): '.format(fname)
        self.msg_bar()
        key = self.window.getch()
        if key in [ord('Y'),ord('y')]:
            self.player.name = entry
            attrs = self.player.attributes[0]
            with open(fname, 'w+') as outf:
                json.dump(
                        self.package_entity(),
                        outf
                        )
            self.current_msg = '{} saved!'.format(fname)
            self.attr_init()
            return False
        else:
            self.current_msg = 'Entity save aborted!'
            self.msg_bar()
            return True

    def package_entity(self):
        return {
            'name':self.player.name,
            'class':self.player.player_class.__class__.__name__,
            'attributes':{attr:getattr(self.player,attr) for attr in self.player.attributes[0]},
            'resists':{res:getattr(self.player,res) for res in self.player.resists[0]},
            'meta':{fl:getattr(self.player,fl) for fl in ('level','spells','sneaks','damage')},
            'status':{st:getattr(self.player,st) for st in self.player.status_effects[0]}
            }

    def print_item_list(self):
        self.window.addstr(self.margin,2,'Attributes ({})'.format(
                                            self.player.free_attr),
                                            self.info_msg | curses.A_BOLD
                                            )
        for idx, item in enumerate(self.items):
            attr, val = item
            if idx == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL

            self.window.addstr(self.margin+idx+1,2,attr,mode)
            self.window.addstr(self.margin+idx+1,17,str(val).rjust(2),mode)

    def print_resist_list(self):
        self.window.addstr(self.margin+11,2,'Resists',self.info_msg | curses.A_BOLD)
        for i,resist in enumerate(self.player.resists[0]):
            self.window.addstr(
                    self.margin+12+i,2,
                    resist,
                    curses.color_pair(1)
                    )
            self.window.addstr(
                    self.margin+12+i,17,
                    str(getattr(self.player,resist)).rjust(2),
                    curses.color_pair(1)
                    )

    def print_player_stats(self):

        def _print_stat(s):
            self.window.addstr(self.margin+i,22,s,mode)
            self.window.addstr(
                           self.margin+i,37,
                           str(self.player.get_stat(s)).rjust(2),
                           mode
                           )

        mode = curses.color_pair(1)
        self.window.addstr(self.margin,22,'Player Stats',
                           self.info_msg | curses.A_BOLD
                           )
        i = 1
        __stats = self.player.player_stats
        for calc_stat in [s for s in __stats if not __stats[s][1]]:
            _print_stat(calc_stat)
            i += 1

        for stat in [s for s in __stats if __stats[s][1]]:
            _print_stat(stat)
            i += 1

        _print_stat('max_damage')

    def attribute_info(self):
        title = self.over
        desc = self.player.attr_desc[title]
        self.draw_sidewin(title,desc)

class ClassSelection(AttributeSelection):

    def post_init(self, player):
       self.player = player
       self.side_win, self.desc_panel = self.side_panel(20,60,2,40)
       self.items = [(pc.__name__,pc) for pc in CLASSES]
       self.items.append(('Done',''))

    def print_item_list(self):
        self.window.addstr(self.margin,2,'Player Classes',
                                self.info_msg | curses.A_BOLD)
        for idx, item in enumerate(self.items):
            cls_name, cls = item
            if idx == self.position:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL

            self.window.addstr(self.margin+idx+2,2,cls_name,mode)

    def main_loop(self):
        if self.player.player_class is not None:
            return
        self.position=3
        while True:
            # Loop init, refresh windows and print menus
            self._loop_start()
            # Print menu items
            self.print_item_list()
            # Print the menu bar (Save/Quit)
            self.menu_bar()

            if not self.first_pass:
                if not self.process_selection(self.window.getch()):
                    break

            self.first_pass = False

            self.debug_info()
            self.msg_bar()

    def process_selection(self,key):
        if key in [curses.KEY_ENTER, ord('\n')]:
            if self.position == len(self.items)-1:
                self.over=None
                return False
            else:
                self.player.player_class = self.items[self.position][1]()
                self.player.player_class._select(self.player)
                self.current_msg = 'Class selected: {}'.format(
                                        self.items[self.position][0])
                self.msg_bar()
                return False

        elif key == curses.KEY_UP:
            self.navigate(-1)

        elif key == curses.KEY_DOWN:
            self.navigate(1)

        elif key in [ord('S'),ord('s')]:
            self.current_msg = 'You must select Attributes before saving!'
            return True

        elif key in [ord('Q'),ord('q')]:
            self.over=None
            return False

        if self.position < len(self.items)-1:
            cls = self.items[self.position][1]
            self.over = cls.__name__
            self.class_info(cls)
            self.current_msg = 'Hit ENTER to select this class'
        else:
            self.clear_sidewin()
            self.over = 'done'
            self.current_msg = 'Hit ENTER to return to the previous menu'

        return True

    def class_info(self,cls):
        title = self.over
        desc = cls.description
        self.draw_sidewin(title,desc)

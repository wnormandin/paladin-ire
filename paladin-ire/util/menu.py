import curses
import json
from curses import panel
import random

from player.attributes import ATTRIBUTE_DESCRIPTIONS as attr_desc
from player.core import RandomRoll as roll
from player.core import NAME_LIST

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

    def _pre_draw(self,yv,xv):
        self.window.move(yv,xv)
        self.window.clrtoeol()

    def debug_info(self):

        yval,xval = curses.getsyx()
        y = self.maxy-3
        x = self.maxx-22

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
                key = self.window.getch()
            else:
                key = None
                self.first_pass = False

            if key in [curses.KEY_ENTER, ord('\n')]:
                if self.position == len(self.items)-1:
                    break
                else:
                    self.items[self.position].hook()

            elif key == curses.KEY_UP:
                self.navigate(-1)

            elif key == curses.KEY_DOWN:
                self.navigate(1)

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

    @property
    def free_attr(self):
        attr_sum = 0
        for attr in self.player.attributes[0]:
            attr_sum += int(getattr(self.player, attr))
        return ((self.player.level * 10) + 7) - attr_sum

    def attr_init(self):
        # rolls initial player attributes
        rr = roll(self.player, 5)
        while True:
            for a in self.player.attributes[0]:
                setattr(self.player, a, rr.roll(None))
            if self.free_attr == 5: break
        self.refresh_attributes()

    def post_init(self, player):
        self.player = player
        self.refresh_attributes()
        self.side_win, self.desc_panel = self.side_panel(12, 24, 2, 48)

    def refresh_attributes(self):
        attrs, _ = self.player.attributes
        self.items = [(attr, getattr(self.player,attr)) for attr in attrs]
        self.items.extend([('Re-roll',''),('Done','')])

    def side_panel(self, h, l, y, x):
        win = curses.newwin(h,l,y,x)
        win.erase()
        win.box()
        panel = curses.panel.new_panel(win)
        return win, panel

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

    def draw_sidewin(self,title,msg):
        self._pre_draw(2,2)
        self.side_win.addstr(2,self.margin+1,title, curses.A_BOLD | curses.color_pair(3))
        i = self.margin+1
        self.clear_sidewin()
        for line in msg.split('\n'):
            self.side_win.addstr(i,self.margin+1,line)
            i += 1

    def clear_sidewin(self):
        for j in range(self.side_win.getmaxyx()[0]):
            self._pre_draw(j,2)

    def _loop_start(self):
        self.window.refresh()
        self.window.box()
        self.side_win.overlay(self.window)
        self._draw_desc()
        curses.doupdate()

    def main_loop(self):
        self.position=8
        while True:
            # Loop init, refresh windows and print menus
            self._loop_start()
            self.print_item_list()
            self.print_resist_list()
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
                self.attr_init()
                self.print_item_list()
                self.current_msg = 'Attributes re-rolled'
                self.msg_bar()
                return True
            else:
                if self.free_attr > 0:
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
            self.save_entity()
            return True

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
            attrs = self.player.attributes[0]
            with open(fname, 'w+') as outf:
                json.dump(
                        {attr:getattr(self.player,attr) for attr in attrs},
                        outf
                        )
            self.current_msg = '{} saved!'.format(fname)
            self.attr_init()
        else:
            self.current_msg = 'Entity save aborted!'
            self.msg_bar

    def print_item_list(self):
        self.window.addstr(self.margin,2,'Attributes ({})'.format(self.free_attr),
                                           self.info_msg | curses.A_BOLD)
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

    def attribute_info(self):
        title = self.over
        desc = self.player.attr_desc[title]
        self.draw_sidewin(title,desc)

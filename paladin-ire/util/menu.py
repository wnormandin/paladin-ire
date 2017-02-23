import curses
from curses import panel

from player.attributes import ATTRIBUTE_DESCRIPTIONS as attr_desc

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
        self.current_msg = None
        self.first_pass = True
        self.over = None

    def msg_bar(self,msg=' '):
        yval,xval = self.window.getmaxyx()
        col = self.hlt_msg
        self.window.addstr(
            yval-2,
            self.margin,
            self.current_msg.ljust(xval-2, ' '),
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

        self.margin = 2

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
        return ((self.player.level * 7) + 10) - attr_sum

    def post_init(self, player):
        self.player = player
        self.refresh_attributes()
        self.side_win, self.desc_panel = self.side_panel(12, 24, 2, 48)

    def refresh_attributes(self):
        attrs, _ = self.player.attributes
        self.items = [(attr, getattr(self.player,attr)) for attr in attrs]
        self.items.append(('Done',''))

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

    def draw_sidewin(self,title,msg='test'):
        self._pre_draw(2,2)
        self.side_win.addstr(2,self.margin+1,title, curses.A_BOLD | curses.color_pair(333))
        i = self.margin+1
        for j in range(self.side_win.getmaxyx()[0]):
            self._pre_draw(j,2)
        for line in msg.split('\n'):
            self.side_win.addstr(i,self.margin+1,line)
            i += 1

    def _loop_start(self):
        self.window.refresh()
        self.window.box()
        self.side_win.overlay(self.window)
        self._draw_desc()
        curses.doupdate()

    def main_loop(self):
        self.position=6
        while True:
            # Loop init, refresh windows and print menus
            self._loop_start()
            self.print_item_list()
            self.print_resist_list()

            if not self.first_pass:
                if not self.process_selection(self.window.getch()):
                    break
            else:
                self.current_msg = 'Press ENTER to return to the previous menu'

            self.first_pass = False

            self.debug_info()
            self.msg_bar()

    def process_selection(self,key):
        if key in [curses.KEY_ENTER, ord('\n')]:
            if self.position == len(self.items)-1:
                self.over=None
                return False
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

        if self.position != len(self.items)-1:
            self.over = self.player.attributes[0][self.position]
            self.attribute_info()
            self.current_msg = 'Hit ENTER to increase this attribute'
        else:
            self.over = None
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

    def print_item_list(self):
        self.window.addstr(2,2,'Attributes ({})'.format(self.free_attr),
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
        self.window.addstr(11,2,'Resists',self.info_msg | curses.A_BOLD)
        for i,resist in enumerate(self.player.resists[0]):
            self.window.addstr(
                    12+i,2,
                    resist,
                    curses.color_pair(1)
                    )
            self.window.addstr(
                    12+i,17,
                    str(getattr(self.player,resist)).rjust(2),
                    curses.color_pair(1)
                    )

    def attribute_info(self):
        title = self.over
        desc = self.player.attr_desc[title]
        self.draw_sidewin(title,desc)

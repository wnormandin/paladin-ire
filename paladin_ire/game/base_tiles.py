import curses


class BaseTile(object):

    def __init__(self):
        self.char = ' '
        self.passable = False   # allow/deny entity traversal of tile
        self.visited = False    # indicate whether player has visited tile
        self.items = []         # list of items on tile
        self.entities = []      # contained entity list
        self.color = None
        self.a_mode = curses.A_NORMAL
        self.post_init()

    @property
    def has_player(self):
        retval = True if any(e.__class__ == 'Player' for e in self.entities) \
                else False
        return retval

    def get_char(self, key):
        try:
            # Return the integer equivalent curses.ACS_<key>
            return acs_chars[key][1]
        except KeyError:
            return '!'

    def get_col(self, col):
        try:
            # return the color pair curses.color_pair(X)
            return col_pairs[col]
        except KeyError:
            return curses.color_pair(0)

    def post_init(self): pass

    @property
    def mode(self):
        retval = self.a_mode if self.color is None \
                 else self.a_mode | self.color
        return retval


class Wall(BaseTile):

    def post_init(self):
        self.char = self.get_char('board')
        self.a_mode = curses.A_DIM
        self.color = curses.COLOR_GRAY


class Hallway(BaseTile):

    def post_init(self):
        pass

def tile_test(scr):
    # Prints the acs_chars list of characters and exits
    win = scr.subwin(0, 0)
    win.keypad(1)

    i = 2
    for key in acs_chars:
        win.addch(2, i, getattr(curses, acs_chars[key][0]))
        i += 2

    win.refresh()
    win.getch()

col_pairs = {
    'cyan': curses.color_pair(1),
    'red': curses.color_pair(2),
    'green': curses.color_pair(3),
    'highlight': curses.color_pair(4),
    'bold': curses.color_pair(5)
    }

acs_chars = {
    'bbss': ('ACS_BBSS', 4194411),
    'block': ('ACS_BLOCK', 4194352),
    'board': ('ACS_BOARD', 4194408),
    'bsbs': ('ACS_BSBS', 4194417),
    'bssb': ('ACS_BSSB', 4194412),
    'bsss': ('ACS_BSSS', 4194423),
    'btee': ('ACS_BTEE', 4194422),
    'bullet': ('ACS_BULLET', 4194430),
    'ckboard': ('ACS_CKBOARD', 4194401),
    'darrow': ('ACS_DARROW', 4194350),
    'degree': ('ACS_DEGREE', 4194406),
    'diamond': ('ACS_DIAMOND', 4194400),
    'gequal': ('ACS_GEQUAL', 4194426),
    'hline': ('ACS_HLINE', 4194417),
    'lantern': ('ACS_LANTERN', 4194409),
    'larrow': ('ACS_LARROW', 4194348),
    'lequal': ('ACS_LEQUAL', 4194425),
    'llcorner': ('ACS_LLCORNER', 4194413),
    'lrcorner': ('ACS_LRCORNER', 4194410),
    'ltee': ('ACS_LTEE', 4194420),
    'nequal': ('ACS_NEQUAL', 4194428),
    'pi': ('ACS_PI', 4194427),
    'plminus': ('ACS_PLMINUS', 4194407),
    'plus': ('ACS_PLUS', 4194414),
    'rarrow': ('ACS_RARROW', 4194347),
    'rtee': ('ACS_RTEE', 4194421),
    's1': ('ACS_S1', 4194415),
    's3': ('ACS_S3', 4194416),
    's7': ('ACS_S7', 4194418),
    's9': ('ACS_S9', 4194419),
    'sbbs': ('ACS_SBBS', 4194410),
    'sbsb': ('ACS_SBSB', 4194424),
    'sbss': ('ACS_SBSS', 4194421),
    'ssbb': ('ACS_SSBB', 4194413),
    'ssbs': ('ACS_SSBS', 4194422),
    'sssb': ('ACS_SSSB', 4194420),
    'ssss': ('ACS_SSSS', 4194414),
    'sterling': ('ACS_STERLING', 4194429),
    'ttee': ('ACS_TTEE', 4194423),
    'uarrow': ('ACS_UARROW', 4194349),
    'ulcorner': ('ACS_ULCORNER', 4194412),
    'urcorner': ('ACS_URCORNER', 4194411),
    'vline': ('ACS_VLINE', 4194424)
    }

if __name__=='__main__':
    curses.wrapper(tile_test)

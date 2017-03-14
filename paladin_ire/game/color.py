# With the Color class, color_wrap provides limited color, underline, and boldface
# type when outputting to consoles or logs
def color_wrap(val, color):
	return '{}{}{}'.format(color, val, '\033[0m')

# Limited selection
# Uses ascii color codes, may not play nicely with all terminals
class Color:
    BLACK_ON_GREEN = '\x1b[1;30;42m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

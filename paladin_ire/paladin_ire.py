#!/usr/bin/env python3.6

import argparse
import curses
import signal
import sys
import termios
import tty

from game.player import Player
from scripts.player_creation import MainMenu

this = sys.modules[__name__]


def parse_args():
    def _test_args(args):
        x, y = args.dimensions[0], args.dimensions[1]
        if x < 130:
            print(
                '[!] X ({}) smaller than the min (130), setting X=130'.format(
                    x))
            args.dimensions[0] = 130
        if y < 30:
            print(
                '[!] Y ({}) smaller than the min (30), setting Y=30'.format(y))
            args.dimensions[1] = 30
        if args.debug and args.verbose < 1:
            print('[!] Debug mode detected, forcing verbose output')
            args.verbose = 1
        return args

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--create', action='store_true',
                        help='Create a new character')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Debug run')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='More verbose output, -vvv = max verbosity')
    parser.add_argument('--dimensions', nargs=2, default=[140, 40],
                        help='Console dimensions, defaults to 140x40, min 130x30')
    parser.add_argument('--difficulty', type=int, default=1,
                        help='Game difficulty (default=1:Easy)')
    return _test_args(parser.parse_args())


def console_prompt(msg=None):
    """ Switch to unbuffered mode and read one char with optional prompt """

    if msg is not None:
        print(msg)
    else:
        print('Press any key to continue')

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if ch == '\x03':
        raise KeyboardInterrupt
    return ch


def graceful_exit(*args):
    signal.signal(signal.SIGINT, this.signal_orig)
    # Graceful exit stuff here
    raise KeyboardInterrupt


class GameApp(object):
    """
    Primary game application class,
    handles pre- and post- execution operations,
    """

    def __init__(self):
        # Capture Ctrl+C immediately, rather than waiting for
        # Python to catch it
        this.signal_orig = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, graceful_exit)

        # Parse the command-line arguments
        self.args = parse_args()

    def __curses_init(self):

        def resize_terminal():
            x, y = self.args.dimensions[0], self.args.dimensions[1]
            if self.args.verbose > 0:
                print("[*] Resizing the terminal to y:{},x:{}".format(y, x))
            try:
                sys.stdout.write("\x1b[8;{};{}t".format(y, x))
            except Exception as e_inner:
                if self.args.debug:
                    raise
                if self.args.verbose > 0:
                    print("[*] Terminal resize failed: {}".format(str(e_inner)))

        def color_init():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLUE)
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)

        color_init()
        curses.curs_set(0)
        resize_terminal()

    def __window_launcher(self, stdscreen, target, player):
        # Should be the target for each windowed process
        # using curses.wrapper()
        self.__curses_init()
        target(stdscreen, player, self)

    def execute(self):
        self.player = Player()
        if self.args.create:
            curses.wrapper(self.__window_launcher, MainMenu, self.player)
            sys.exit(0)
        if self.args.debug:
            print('\n[*] Paladin-Ire running in Debug mode')
            print('[*] Spawning a player')
            print('[*] Pre-game checks complete')
            console_prompt('Press any key for the main menu')
            curses.wrapper(self.__window_launcher, MainMenu, self.player)
            sys.exit(0)


if __name__ == "__main__":
    app = None
    try:
        app = GameApp()
        if app.args.debug:
            print('[*] Executing...')
        app.execute()

    except (KeyboardInterrupt, SystemExit):
        if app is not None:
            if app.args.verbose > 0:
                print('[!] Keyboard interrupt or system exit detected, quitting')
                sys.exit(1)

    except Exception as e:
        if app is None:
            raise
        if app.args.debug:
            raise
            # pdb.post_mortem()
        elif app.args.verbose:
            print(str(e))
        else:
            print("[!] Unhandled exception detected, exiting")
            raise

#!/usr/bin/env python3.6

import logging
import tty, termios, sys
from scripts.player_creation import character_creation
from player.player import Player
import argparse
import pdb
import signal

this = sys.modules[__name__]

def parse_args():

    def _test_args(args):
        x, y = args.dimensions[0], args.dimensions[1]
        if x < 130:
            print('[!] X dimension ({}) smaller than the minimum (130), setting X=130'.format(x))
            args.dimensions[0]=130
        if y < 30:
            print('[!] Y dimension ({}) smaller than the minimum (30), setting Y=30'.format(y))
            args.dimensions[1]=30
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
    parser.add_argument('--dimensions',nargs=2, default=[140,40],
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

    fd=sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '\x03':
        raise KeyboardInterrupt
    return ch

def graceful_exit(num, frame):
    signal.signal(signal.SIGINT, signal_orig)
    # Graceful exit stuff here
    raise KeyboardInterrupt

if __name__ == "__main__":
    try:
        # Capture Ctrl+C immediately, rather than waiting for
        # Python to catch it
        this.signal_orig = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, graceful_exit)

        # Parse and validate arguments
        args = parse_args()

        # Set the tty size, may not function on all terminals
        if args.verbose > 0:
            print("[*] Resizing the terminal")
        try:
            sys.stdout.write("\x1b[8;{};{}t".format(
                        args.dimensions[1], args.dimensions[0])
                        )
        except:
            if args.debug: raise
            if args.verbose > 0:
                print("[*] Terminal resize failed")

        if args.create:
            # Runs the (main) menu currently, adapt to
            # allow creation of arbitrary NPCs
            p = Player()
            character_creation(p, args)
            sys.exit(0)

        if args.debug:
            print("\n[*] Paladin-Ire Debug Run Initiated")
            console_prompt()
            print("[*] Spawning player")

        p = Player()

        if args.debug:
            print("[*] Pre-game checks complete")
            console_prompt('Press any key for the game menu')

        # Enter the character creation menu
        character_creation(p, args)

    except (KeyboardInterrupt, SystemExit):
        if args.verbose > 0:
            print('[!] Keyboard interrupt or system exit detected, quitting')
            sys.exit(1)

    except Exception as e:
        if args is None: raise
        if args.debug:
            raise
            #pdb.post_mortem()
        elif args.verbose:
            print(e[0])
        else:
            raise
            print("[!] Unhandled exception detected, exiting")

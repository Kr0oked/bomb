__author__ = 'Philipp Bobek'
__copyright__ = 'Copyright (C) 2015 Philipp Bobek'
__license__ = 'Public Domain'
__version__ = '1.0'

import argparse
import time
from Adafruit_LEDBackpack.SevenSegment import SevenSegment


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bomb Mock-up')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='store_false', dest='verbose',
                        help='print full output messages [default]')
    parser.add_argument('-t', '--time', type=int, dest='time', default=60,
                        help='time until the bomb explodes')
    parser.add_argument('-u', '--url', type=str, dest='url', default='localhost/bomb',
                        help='url to call when the bomb explodes')
    args = parser.parse_args()

    segment = SevenSegment(0x70, args.verbose)

    print "Press CTRL+Z to exit"

    i = 0
    while args.time >= 0:
        if args.verbose:
            print time

        # todo: beep

        segment.write_digit(0, 0)
        segment.write_digit(1, 0)
        segment.write_digit(3, 3)
        segment.write_digit(4, 0)
        segment.set_colon(True)

        i -= 1

        time.sleep(1)

    # todo: call url

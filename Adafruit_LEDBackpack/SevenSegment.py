__author__ = 'Philipp Bobek'
__copyright__ = 'Copyright (C) 2015 Philipp Bobek'
__license__ = 'Public Domain'
__version__ = '1.0'

from Adafruit_LEDBackpack.LEDBackpack import LEDBackpack


class SevenSegment:
    display = None
    digits = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F, 0x77, 0x7C, 0x39, 0x5E, 0x79, 0x71]

    def __init__(self, address=0x70, debug=False):
        if debug:
            print "Initializing a new instance of LEDBackpack at 0x%02X" % address
        self.display = LEDBackpack(address=address, debug=debug)

    def write_digit_raw(self, char_number, value):
        """Sets a digit using the raw 16-bit value"""
        if char_number > 7:
            return
        self.display.set_buffer_row(char_number, value)

    def write_digit(self, char_number, value, dot=False):
        """Sets a single decimal or hex value (0..9 and A..F)"""
        if char_number > 7:
            return
        if value > 0xF:
            return
        self.display.set_buffer_row(char_number, self.digits[value] | (dot << 7))

    def set_colon(self, state=True):
        """Enables or disables the colon character"""
        if state:
            self.display.set_buffer_row(2, 0xFFFF)
        else:
            self.display.set_buffer_row(2, 0)

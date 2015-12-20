__author__ = 'Philipp Bobek'
__copyright__ = 'Copyright (C) 2015 Philipp Bobek'
__license__ = 'Public Domain'
__version__ = '1.0'

from copy import copy
from Adafruit_I2C.I2C import I2C


class LEDBackpack:
    i2c = None

    # Registers
    __HT16K33_REGISTER_DISPLAY_SETUP = 0x80
    __HT16K33_REGISTER_SYSTEM_SETUP = 0x20
    __HT16K33_REGISTER_DIMMING = 0xE0

    # Data base addresses
    __HT16K33_ADDRESS_KEY_DATA = 0x40

    # Blink rate
    __HT16K33_BLINKRATE_OFF = 0x00
    __HT16K33_BLINKRATE_2HZ = 0x01
    __HT16K33_BLINKRATE_1HZ = 0x02
    __HT16K33_BLINKRATE_HALFHZ = 0x03

    # Display buffer (8x16-bits)
    __buffer = [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000]

    # Constructor
    def __init__(self, address=0x70, debug=False):
        self.i2c = I2C(address)
        self.address = address
        self.debug = debug

        # Turn the oscillator on
        self.i2c.write8(self.__HT16K33_REGISTER_SYSTEM_SETUP | 0x01, 0x00)

        # Turn blink off
        self.set_blink_rate(self.__HT16K33_BLINKRATE_OFF)

        # Set maximum brightness
        self.set_brightness(15)

        # Clear the screen
        self.clear()

    def set_brightness(self, brightness):
        """Sets the brightness level from 0..15"""
        if brightness > 15:
            brightness = 15
        self.i2c.write8(self.__HT16K33_REGISTER_DIMMING | brightness, 0x00)

    def set_blink_rate(self, blink_rate):
        """Sets the blink rate"""
        if blink_rate > self.__HT16K33_BLINKRATE_HALFHZ:
            blink_rate = self.__HT16K33_BLINKRATE_OFF
        self.i2c.write8(self.__HT16K33_REGISTER_DISPLAY_SETUP | 0x01 | (blink_rate << 1), 0x00)

    def set_buffer_row(self, row, value, update=True):
        """Updates a single 16-bit entry in the 8*16-bit buffer"""
        if row > 7:
            return  # Prevent buffer overflow
        self.__buffer[row] = value  # value # & 0xFFFF
        if update:
            self.write_display()  # Update the display

    def get_buffer_row(self, row):
        """Returns a single 16-bit entry in the 8*16-bit buffer"""
        if row > 7:
            return
        return self.__buffer[row]

    def get_buffer(self):
        """Returns a copy of the raw buffer contents"""
        buffer_copy = copy(self.__buffer)
        return buffer_copy

    def write_display(self):
        """Updates the display memory"""
        display_memory = []
        for item in self.__buffer:
            display_memory.append(item & 0xFF)
            display_memory.append((item >> 8) & 0xFF)
        self.i2c.write_list(0x00, display_memory)

    def get_keys(self, row):
        """Returns a row of scanned key press values as a single 13-bit value (K13:K1)"""
        if row > 2:
            return
        return self.i2c.read_u16(self.__HT16K33_ADDRESS_KEY_DATA + row * 2)

    def clear(self, update=True):
        """Clears the display memory"""
        self.__buffer = [0, 0, 0, 0, 0, 0, 0, 0]
        if update:
            self.write_display()


led = LEDBackpack(0x70)

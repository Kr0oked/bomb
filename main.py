#!/usr/bin/python

import argparse
import re
import requests
import RPi.GPIO as GPIO
from time import sleep
from requests.exceptions import ConnectionError
from Adafruit_LEDBackpack.SevenSegment import SevenSegment
from digits import Digits

__author__ = 'Philipp Bobek'
__copyright__ = 'Copyright (C) 2015 Philipp Bobek'
__license__ = 'Public Domain'
__version__ = '1.0'


def parse_args():
    parser = argparse.ArgumentParser(description='Bomb Mock-up')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-v', '--verbose', action='store_false', dest='verbose',
                        help='print full output messages [default]')
    parser.add_argument('-t', '--time', type=int, dest='time', default=180,
                        help='time in seconds until the bomb explodes')
    parser.add_argument('-u', '--url', type=str, dest='url', default='http://localhost/bomb',
                        help='url to call when the bomb explodes')
    parser.add_argument('-b', '--brightness', type=int, dest='brightness', default=15,
                        help='sets the brightness of the display, 0 is the least bright and 15 is the brightest')
    parser.add_argument('-r', '--rate', type=int, dest='blink_rate', default=0,
                        help='sets the blink rate of the display, 0 is no blinking and 1,2 or 3 is for blinking')
    return parser.parse_args()


def is_time_valid(time_in_seconds):
    return 0 <= time_in_seconds <= 3600


def is_url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if regex.match(url) is None:
        return False
    return True


def is_brightness_valid(brightness):
    return 0 <= brightness <= 15


def is_blink_rate_valid(blink_rate):
    return 0 <= blink_rate <= 3


def check_arguments(arguments):
    if not is_time_valid(arguments.time):
        print("Invalid time value: " + str(arguments.time))
        exit()

    if not is_url_valid(arguments.url):
        print("Invalid url: " + arguments.url)
        exit()

    if not is_brightness_valid(arguments.brightness):
        print("Invalid brightness: " + str(arguments.brightness))
        exit()

    if not is_blink_rate_valid(arguments.blink_rate):
        print("Invalid blink rate: " + str(arguments.blink_rate))
        exit()


def wait_for_button_press_and_release():
    try:
        print("Wait for button press")
        GPIO.wait_for_edge(4, GPIO.FALLING)
        print("Button press detected")
        print("Wait for button release")
        GPIO.wait_for_edge(4, GPIO.RISING)
        print("Button release detected")
    except RuntimeError as exception:
        print("An exception occurred while waiting for an edge")
        print(repr(exception))
        wait_for_button_press_and_release()


def get_digits(time_in_seconds):
    minutes = int(time_in_seconds / 60)
    seconds = time_in_seconds % 60

    digit_one = int(minutes / 10)
    digit_two = minutes % 10
    digit_three = int(seconds / 10)
    digit_four = seconds % 10

    return Digits(digit_one, digit_two, digit_three, digit_four)


def call_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Call to " + url + " returned OK")
        else:
            print("Call to " + url + " returned status code " + str(response.status_code))
    except ConnectionError as exception:
        print("An exception occurred during the call to " + url)
        print(repr(exception))
    # todo: Backup solution


def main():
    args = parse_args()
    check_arguments(args)

    segment = SevenSegment(0x70, args.verbose)
    segment.display.set_brightness(args.brightness)
    segment.display.set_blink_rate(args.blink_rate)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(14, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.output(15, True)

    print("Press CTRL+C to exit")

    while True:

        wait_for_button_press_and_release()

        seconds_left = args.time
        while seconds_left >= 0:
            digits = get_digits(seconds_left)

            if args.verbose:
                print(str(digits.one) + str(digits.two) + ":" + str(digits.three) + str(digits.four))

            segment.write_digit(0, digits.one)
            segment.write_digit(1, digits.two)
            segment.write_digit(3, digits.three)
            segment.write_digit(4, digits.four)
            segment.set_colon(True)

            GPIO.output(14, seconds_left % 2 == 0)

            # todo: beep

            seconds_left -= 1
            sleep(1)

        call_url(args.url)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()

# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Simple blocking event loop reads built in button and turns LED on and off based
on line edge. If you do not pass in --led then only button status is displayed.
-------------
Should work on any board with a button built in. Just change chip and line
value as needed.
"""

import sys, time, gpiod
from argparse import *


class buttonpress:
    
    def __init__(self, chip_button, chip_led):
        """Handle possibility of button and led on different GPIO chips
        """         
        self.chip_button = gpiod.Chip(chip_button, gpiod.Chip.OPEN_BY_PATH)
        if chip_led != chip_button:
            self.chip_led = gpiod.Chip(chip_led, gpiod.Chip.OPEN_BY_PATH)
        else:
            self.chip_led = self.chip_button

    def main(self, button, led):
        """Print edge events for 10 seconds.
        """         
        print("Button name: %s, label: %s, lines: %d" % (self.chip_button.name(), self.chip_button.label(), self.chip_button.num_lines()))
        print("LED name: %s, label: %s, lines: %d" % (self.chip_led.name(), self.chip_led.label(), self.chip_led.num_lines()))
        button_line = self.chip_button.get_line(button)
        button_line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        if led:
            led_line = self.chip_led.get_line(led)
            led_line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_DIR_OUT)
        else:
            led_line = None    
        print("Press and release button, timeout in 10 seconds after last press\n")
        while button_line.event_wait(sec=10):
            event = button_line.event_read()
            if event.type == gpiod.LineEvent.RISING_EDGE:
                print("Rising  edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
            elif event.type == gpiod.LineEvent.FALLING_EDGE:
                print("Falling edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
            else:
                raise TypeError('Invalid event type')
            # If led arg passed then turn on and off based on event type
            if led_line:
                if event.type == gpiod.LineEvent.RISING_EDGE:
                    led_line.set_value(1)
                else:
                    led_line.set_value(0)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip_button", help="GPIO chip name (default '/dev/gpiochip1')", type=str, default="/dev/gpiochip1")
    parser.add_argument("--button", help="GPIO line number (default 3 button on NanoPi Duo)", type=int, default=3)
    parser.add_argument("--chip_led", help="GPIO chip name (default '/dev/gpiochip0')", type=str, default="/dev/gpiochip0")
    parser.add_argument("--led", help="GPIO line number", type=int)
    args = parser.parse_args()
    obj = buttonpress(args.chip_button, args.chip_led)
    obj.main(args.button, args.led)

# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Simple blocking event loop example.
-------------
Should work on any board with a button built in. Just change chip and line
value as needed.
"""

import sys, time, gpiod
from argparse import *


class buttonpress:
    
    def __init__(self, chip):
        """Create library and ffi interfaces.
        """         
        self.chip = gpiod.Chip(chip, gpiod.Chip.OPEN_BY_PATH)

    def show_event(self, event):
        if event.type == gpiod.LineEvent.RISING_EDGE:
            print("Rising  edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
        elif event.type == gpiod.LineEvent.FALLING_EDGE:
            print("Falling edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
        else:
            raise TypeError('Invalid event type')

    def main(self, button, led):
        """Print edge events for 10 seconds.
        """         
        print("Name: %s, label: %s, lines: %d" % (self.chip.name(), self.chip.label(), self.chip.num_lines()))
        button_line = self.chip.get_line(button)
        button_line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        if led:
            led_line = self.chip.get_line(led)
            led_line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_DIR_OUT)
        print("Press and release button, timeout in 10 seconds\n")
        while button_line.event_wait(sec=10):
            event = button_line.event_read()
            self.show_event(event)
            # If led arg passed then turn on and off based on event type
            if led_line:
                if event.type == gpiod.LineEvent.RISING_EDGE:
                    led_line.set_value(1)
                else:
                    led_line.set_value(0)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip name (default '/dev/gpiochip1')", type=str, default="/dev/gpiochip1")
    parser.add_argument("--button", help="GPIO line number (default 3 button on NanoPi Duo)", type=int, default=3)
    parser.add_argument("--led", help="GPIO line number (default 203 IOG11 on NanoPi Duo)", type=int, default=203)
    args = parser.parse_args()
    obj = buttonpress(args.chip)
    obj.main(args.button, args.led)

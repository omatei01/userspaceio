# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Use libgpiod context less event loop to implement blocking callback
-------------
Should work on any board with a button built in. Just change chip and line
value as needed.
"""

import sys, time, gpiod
from argparse import *


class buttoncallback:
    
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

    def main(self, line):
        """Print edge events for 10 seconds.
        """         
        print("Name: %s, label: %s, lines: %d" % (self.chip.name(), self.chip.label(), self.chip.num_lines()))
        line = self.chip.get_line(line)
        line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        print("Press and release button, timeout in 10 seconds\n")
        while line.event_wait(sec=10):
            event = line.event_read()
            self.show_event(event)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip name (default '/dev/gpiochip1')", type=str, default="/dev/gpiochip1")
    parser.add_argument("--line", help="GPIO line number (default 3 button on NanoPi Duo)", type=int, default=3)
    args = parser.parse_args()
    obj = buttoncallback(args.chip)
    obj.main(args.line)

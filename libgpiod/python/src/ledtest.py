# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Simple LED blink
-------------
Using the NanoPi Duo connect a 220Ω resistor to the anode (the long pin of
the LED), then the resistor to 3.3 V, and connect the cathode (the short
pin) of the LED to line 203 (IOG11). The anode of LED connects to a
current-limiting resistor and then to 3.3V. Therefore, to turn on an LED,
we need to make pin 12 low (0V) level.

See images/ledtest.jpg for schematic.
"""

import sys, time, gpiod
from argparse import *


class ledtest:
    
    def __init__(self, chip):
        """Initialize GPIO chip.
        """         
        self.chip = gpiod.Chip(chip, gpiod.Chip.OPEN_BY_NUMBER)
    
    def main(self, line):
        """Turn LED on and off once.
        """
        print("Name: %s, label: %s, lines: %d" % (self.chip.name(), self.chip.label(), self.chip.num_lines()))
        line = self.chip.get_line(line)
        line.request(consumer=sys.argv[0], type=gpiod.LINE_REQ_DIR_OUT)
        line.set_value(0)         
        print("\nLED on")
        time.sleep(3)
        # LED off
        line.set_value(1)
        print("LED off")
        line.release()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip number (default 0 '/dev/gpiochip0')", type=str, default="0")
    parser.add_argument("--line", help="GPIO line number (default 203 IOG11 on NanoPi Duo)", type=int, default=203)
    args = parser.parse_args()
    obj = ledtest(args.chip)
    obj.main(args.line)

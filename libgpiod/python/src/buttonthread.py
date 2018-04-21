# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
Use a thread to monitor edge events in background
-------------
Should work on any board with a button built in. Just change chip and line
value as needed.
"""

import sys, time, threading, gpiod
from argparse import *


class buttonthread:

    def __init__(self, chip):
        """Initialize GPIO chip.
        """         
        self.chip = gpiod.Chip(chip, gpiod.Chip.OPEN_BY_NUMBER)

    def wait_for_edge(self, line, timeoutSecs):
        print("Thread start")
        button_line = self.chip.get_line(line)
        button_line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        while button_line.event_wait(sec=timeoutSecs):
            event = button_line.event_read()
            if event.type == gpiod.LineEvent.RISING_EDGE:
                print("Rising  edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
            elif event.type == gpiod.LineEvent.FALLING_EDGE:
                print("Falling edge timestamp %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
            else:
                raise TypeError('Invalid event type')
        print("Thread exit")

    def main(self, line):
        """Use thread to wait for edge events while main method does other stuff.
        """
        print("Name: %s, label: %s, lines: %d" % (self.chip.name(), self.chip.label(), self.chip.num_lines()))
        # Kick off thread
        thread = threading.Thread(target=self.wait_for_edge, args=(line, 15,))
        thread.start()
        count = 0
        # Just simulating main program doing something else
        while count < 30:
            print("Main program doing stuff, press button")
            time.sleep(1)
            count += 1
        # If thread is still alive wait for it to time out
        if thread.isAlive():
            print("Waiting for thread to exit, stop pressing button for 5 seconds")
            thread.join()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip", help="GPIO chip number (default 1 '/dev/gpiochip1')", type=str, default="1")
    parser.add_argument("--line", help="GPIO line number (default 3 button on NanoPi Duo)", type=int, default=3)
    args = parser.parse_args()
    obj = buttonthread(args.chip)
    obj.main(args.line)

# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
HC-SR501 sensor example
-------------
Monitor rising edge (motion detected) and falling edge (no motion)
"""

import sys, time, gpiod
from argparse import *

class hcsr501:
    
    def __init__(self, chip_sensor, chip_led):
        """Handle possibility of sensor and led on different GPIO chips
        """         
        self.chip_sensor = gpiod.Chip(chip_sensor, gpiod.Chip.OPEN_BY_PATH)
        if chip_led != chip_sensor:
            self.chip_led = gpiod.Chip(chip_led, gpiod.Chip.OPEN_BY_PATH)
        else:
            self.chip_led = self.chip_sensor

    def main(self, sensor, led):
        """Show motion for 30 seconds.
        """
        print("Button name: %s, label: %s, lines: %d" % (self.chip_sensor.name(), self.chip_sensor.label(), self.chip_sensor.num_lines()))
        print("LED name: %s, label: %s, lines: %d" % (self.chip_led.name(), self.chip_led.label(), self.chip_led.num_lines()))
        sensor_line = self.chip_sensor.get_line(sensor)
        sensor_line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_EV_BOTH_EDGES)
        if led:
            led_line = self.chip_led.get_line(led)
            led_line.request(consumer=sys.argv[0][:-3], type=gpiod.LINE_REQ_DIR_OUT)
        else:
            led_line = None
        print("Program will exit after 60 seconds of no activity\n")
        while sensor_line.event_wait(sec=60):
            event = sensor_line.event_read()
            if event.type == gpiod.LineEvent.RISING_EDGE:
                print("Motion detected %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
            elif event.type == gpiod.LineEvent.FALLING_EDGE:
                print("No motion       %s" % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(event.sec)))
            else:
                raise TypeError('Invalid event type')
            # If led arg passed then turn on and off based on event type
            if led_line:
                if event.type == gpiod.LineEvent.RISING_EDGE:
                    led_line.set_value(0)
                else:
                    led_line.set_value(1)            
        print("Timeout exit")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--chip_sensor", help="GPIO chip name (default '/dev/gpiochip1')", type=str, default="/dev/gpiochip1")
    parser.add_argument("--sensor", help="GPIO line number (default 11 GPIOL11/IR-RX on NanoPi Duo)", type=int, default=11)
    parser.add_argument("--chip_led", help="GPIO chip name (default '/dev/gpiochip0')", type=str, default="/dev/gpiochip0")
    parser.add_argument("--led", help="GPIO line number", type=int)
    args = parser.parse_args()
    obj = hcsr501(args.chip_sensor, args.chip_led)
    obj.main(args.sensor, args.led)

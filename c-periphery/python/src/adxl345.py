# -*- coding: utf-8 -*-
# Copyright (c) 2018 Steven P. Goldsmith
# See LICENSE.md for details.

"""
ADXL345 3-Axis, ±2 g/±4 g/±8 g/±16 g digital accelerometer 
-------------
I'm using I2C to communicate with the ADXL345 although SPI is supported as
well.
"""

import sys, time
from argparse import *
from cffi import FFI
from libperiphery import libperipheryi2c
from libgpiod import libgpiod

class adxl345:
    
    def __init__(self):
        """Create library interface.
        """    
        self.i2c = libperipheryi2c.libperipheryi2c()
        self.gpiod = libgpiod.libgpiod()
        self.lib = self.gpiod.lib
        self.ffi = self.gpiod.ffi        
            
    def getRange(self, handle, addr):
        """Retrieve the current range of the accelerometer. See setRange for
        the possible range constant values that will be returned.
        """
        return self.i2c.readReg(handle, addr, 0x31) & 0x03

    def setRange(self, handle, addr, value):
        """Set the range of the accelerometer to the provided value. Read the data
        format register to preserve bits. Update the data rate, make sure that the
        FULL-RES bit is enabled for range scaling.
        """
        regVal = self.i2c.readReg(handle, addr, 0x31) & ~0x0f
        regVal |= value
        regVal |= 0x08  # FULL-RES bit enabled
        # Write the updated format register
        self.i2c.writeReg(handle, addr, 0x31, regVal)
    
    def getDataRate(self, handle, addr):
        """Retrieve the current data rate.
        """
        return self.i2c.readReg(handle, addr, 0x2c) & 0x0f
    
    def setDataRate(self, handle, addr, rate):
        """Set the data rate of the accelerometer. Note: The LOW_POWER bits are
        currently ignored, we always keep the device in 'normal' mode.
        """
        self.i2c.writeReg(handle, addr, 0x2c, rate & 0x0f)
    
    def read(self, handle, addr):
        """Retrieve x, y, z 16 bit data in 6 bytes.
        """
        retVal = self.i2c.readArray(handle, addr, 0x32, 6)
        # Convert to tuple of 16 bit integers x, y, z
        x = retVal[0] | (retVal[1] << 8)
        if(x & (1 << 16 - 1)):
            x = x - (1 << 16)
        y = retVal[2] | (retVal[3] << 8)
        if(y & (1 << 16 - 1)):
            y = y - (1 << 16)
        z = retVal[4] | (retVal[5] << 8)
        if(z & (1 << 16 - 1)):
            z = z - (1 << 16)    
        return (x, y, z)

    def waitForStable(self, handle, addr, maxReads, maxDiff, maxInRange, sleepTime):
        """Wait for unit to become stable or hit maxReads.
        """
        count = 0
        lastX = 0
        lastY = 0
        lastZ = 0
        inRange = 0
        while count < maxReads and inRange <= maxInRange:
            data = self.read(handle, addr)
            curX = data[0]
            curY = data[1]
            curZ = data[2]
            if abs(curX - lastX) <= maxDiff and abs(curY - lastY) <= maxDiff and abs(curZ - lastZ) <= maxDiff:
                inRange += 1
            else:
                inRange = 0
            lastX = curX
            lastY = curY
            lastZ = curZ
            time.sleep(sleepTime)
            count += 1
        return count < maxReads, (curX, curY, curZ)        

    def main(self, device, address, chip, line):
        print ("libgpiod version %s" % self.ffi.string(self.lib.gpiod_version_string()).decode('utf-8'))
        gpiod_chip = self.lib.gpiod_chip_open_by_number(chip)
        # Verify the chip was opened
        if gpiod_chip != self.ffi.NULL:
            print("Name: %s, label: %s, lines: %d" % (self.ffi.string(gpiod_chip.name).decode('utf-8'), self.ffi.string(gpiod_chip.label).decode('utf-8'), gpiod_chip.num_lines))
            gpiod_line = self.lib.gpiod_chip_get_line(gpiod_chip, line)
            # Verify we have line
            if gpiod_line != self.ffi.NULL:
                consumer = sys.argv[0][:-3]
                # This will set line for output and set initial value (LED off)
                if self.lib.gpiod_line_request_output(gpiod_line, consumer.encode('utf-8'), 1) == 0:
                    handle = self.i2c.open(device)
                    # ADXL345 wired up on port 0x53?
                    if self.i2c.readReg(handle, address, 0x00) == 0xe5:
                        # Enable the accelerometer
                        self.i2c.writeReg(handle, address, 0x2d, 0x08)
                        # +/- 2g
                        self.setRange(handle, address, 0x00)
                        # 100 Hz
                        self.setDataRate(handle, address, 0x0a)
                        print("Range = %d, data rate = %d" % (self.getRange(handle, address), self.getDataRate(handle, address)))
                        count = 0
                        while count < 20:
                            stable, data = self.waitForStable(handle, address, 20, 3, 10, 0.05)                
                            if stable:
                                print("Stable x: %04d, y: %04d, z: %04d" % (data[0], data[1], data[2]))
                                # LED off
                                self.lib.gpiod_line_set_value(gpiod_line, 1)
                            else:
                                print("Not stable before timeout")
                                # LED on
                                self.lib.gpiod_line_set_value(gpiod_line, 0)
                            count += 1
                    else:
                        print("Not ADXL345?")
                    # LED off
                    self.lib.gpiod_line_set_value(gpiod_line, 1)
                    self.i2c.close(handle)
                else:
                    print("Unable to set line %d to output" % line)
                self.lib.gpiod_line_release(gpiod_line)
            else:
                print("Unable to get line %d" % line)
            self.lib.gpiod_chip_close(gpiod_chip)    
        else:
            print("Unable to open chip %d" % chip)
                    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--device", help="I2C device name (default '/dev/i2c-0')", type=str, default="/dev/i2c-0")
    parser.add_argument("--address", help="ADXL345 address (default 0x53)", type=str, default="0x53")
    parser.add_argument("--chip", help="GPIO chip number (default 0 '/dev/gpiochip0')", type=int, default=0)
    parser.add_argument("--line", help="GPIO line number (default 203 IOG11 on NanoPi Duo)", type=int, default=203)
    args = parser.parse_args()
    obj = adxl345()
    # Convert from hex string to int
    address = int(args.address, 16)
    obj.main(args.device, address, args.chip, args.line)

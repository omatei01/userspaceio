package com.codeferm.demo;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import com.codeferm.I2c;
import com.sun.jna.Pointer;

import peripheryi2c.i2c_handle;

/**
 * ADXL345 3-Axis, ±2 g/±4 g/±8 g/±16 g digital accelerometer example. I'm using
 * I2C to communicate with the ADXL345 although SPI is supported as well.
 * 
 * Copyright (c) 2018 Steven P. Goldsmith See LICENSE.md for details.
 */

public class Adxl345 {

	/**
	 * Get data range setting.
	 * 
	 * Register 0x31 -- DATA_FORMAT (Read/Write)
	 * 
	 * These bits set the g range as described below.
	 * 
	 * <pre>
	 * Range Setting
	 * | Setting |  g Range | Value |
	 * |    00   | +/-  2 g |   0   |
	 * |    01   | +/-  4 g |   1   |
	 * |    10   | +/-  8 g |   2   |
	 * |    11   | +/- 16 g |   3   |
	 * </pre>
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @return Range.
	 */
	public short getRange(final I2c i2c, final i2c_handle handle, final short addr) {
		return (short) (i2c.readReg(handle, addr, (short) 0x31) & 0x03);
	}

	/**
	 * Set data range setting. Read the data format register to preserve bits.
	 * Update the data rate, make sure that the FULL-RES bit is enabled for range
	 * scaling.
	 * 
	 * Register 0x31 -- DATA_FORMAT (Read/Write)
	 * 
	 * These bits set the g range as described below.
	 * 
	 * <pre>
	 * g Range Setting
	 * | Setting |  g Range | Value |
	 * |    00   | +/-  2 g |   0   |
	 * |    01   | +/-  4 g |   1   |
	 * |    10   | +/-  8 g |   2   |
	 * |    11   | +/- 16 g |   3   |
	 * </pre>
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param value
	 *            Range.
	 */
	public void setRange(final I2c i2c, final i2c_handle handle, final short addr, final short value) {
		// 0x08 sets fill resolution bit to enabled
		i2c.writeReg(handle, addr, (short) 0x31,
				(short) (((i2c.readReg(handle, addr, (short) 0x31) & ~0x0f) | value) | 0x08));
	}

	/**
	 * Get the device bandwidth rate.
	 * 
	 * Register 0x2C -- BW_RATE (Read/Write)
	 * 
	 * These bits select the device bandwidth and output data rateThe default value
	 * is 0x0A, which translates to a 100 Hz output data rate. An output data rate
	 * should be selected that is appropriate for the communication protocol and
	 * frequency selected. Selecting too high of an output data rate with a low
	 * communication speed results in samples being discarded.
	 * 
	 * <pre>
	 * Typical Current Consumption vs. Data Rate
	 * Output Data Rate (Hz) | Bandwidth (Hz) | Rate Code |   Value   | Idd (uA)
	 *          3200         |      1600      |    1111   | 0xF or 15 |   140
	 *          1600         |       800      |    1110   | 0xE or 14 |    90
	 *           800         |       400      |    1101   | 0xD or 13 |   140
	 *           400         |       200      |    1100   | 0xC or 12 |   140
	 *           200         |       100      |    1011   | 0xB or 11 |   140
	 *           100         |        50      |    1010   | 0xA or 10 |   140
	 *            50         |        25      |    1001   | 0x9 or 9  |    90
	 *            25         |      12.5      |    1000   | 0x8 or 8  |    60
	 *          12.5         |      6.25      |    0111   | 0x7 or 7  |    50
	 *          6.25         |      3.13      |    0110   | 0x6 or 6  |    45
	 *          3.13         |      1.56      |    0101   | 0x5 or 5  |    40
	 *          1.56         |      0.78      |    0100   | 0x4 or 4  |    34
	 *          0.78         |      0.39      |    0011   | 0x3 or 3  |    23
	 *          0.39         |      0.20      |    0010   | 0x2 or 2  |    23
	 *          0.20         |      0.10      |    0001   | 0x1 or 1  |    23
	 *          0.10         |      0.05      |    0000   | 0x0 or 0  |    23
	 * </pre>
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @return Range.
	 */
	public short getDataRate(final I2c i2c, final i2c_handle handle, final short addr) {
		return (short) (i2c.readReg(handle, addr, (short) 0x2c) & 0x0f);
	}

	/**
	 * Set the device bandwidth rate.
	 * 
	 * Register 0x2C -- BW_RATE (Read/Write)
	 * 
	 * These bits select the device bandwidth and output data rate. The default
	 * value is 0x0A, which translates to a 100 Hz output data rate. An output data
	 * rate should be selected that is appropriate for the communication protocol
	 * and frequency selected. Selecting too high of an output data rate with a low
	 * communication speed results in samples being discarded. Note: The LOW_POWER
	 * bits are currently ignored, we always keep the device in 'normal' mode.
	 * 
	 * <pre>
	 * Typical Current Consumption vs. Data Rate
	 * Output Data Rate (Hz) | Bandwidth (Hz) | Rate Code |   Value   | Idd (uA)
	 *          3200         |      1600      |    1111   | 0xF or 15 |   140
	 *          1600         |       800      |    1110   | 0xE or 14 |    90
	 *           800         |       400      |    1101   | 0xD or 13 |   140
	 *           400         |       200      |    1100   | 0xC or 12 |   140
	 *           200         |       100      |    1011   | 0xB or 11 |   140
	 *           100         |        50      |    1010   | 0xA or 10 |   140
	 *            50         |        25      |    1001   | 0x9 or 9  |    90
	 *            25         |      12.5      |    1000   | 0x8 or 8  |    60
	 *          12.5         |      6.25      |    0111   | 0x7 or 7  |    50
	 *          6.25         |      3.13      |    0110   | 0x6 or 6  |    45
	 *          3.13         |      1.56      |    0101   | 0x5 or 5  |    40
	 *          1.56         |      0.78      |    0100   | 0x4 or 4  |    34
	 *          0.78         |      0.39      |    0011   | 0x3 or 3  |    23
	 *          0.39         |      0.20      |    0010   | 0x2 or 2  |    23
	 *          0.20         |      0.10      |    0001   | 0x1 or 1  |    23
	 *          0.10         |      0.05      |    0000   | 0x0 or 0  |    23
	 * </pre>
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @param value
	 *            Data rate.
	 */
	public void setDataRate(final I2c i2c, final i2c_handle handle, final short addr, final short value) {
		i2c.writeReg(handle, addr, (short) 0x2c, (short) (value & 0x0f));
	}

	/**
	 * Convert low and high bytes to 10-bit integer.
	 * 
	 * @param lowByte
	 *            Low byte from register.
	 * @param highByte
	 *            High byte from register.
	 * @return Integer value composed of low and high bytes.
	 */
	public int bytesToInt(final byte lowByte, final byte highByte) {
		// Convert the data to 10-bits
		int value = ((highByte & 0x03) * 256 + (lowByte & 0xff));
		if (value > 511) {
			value -= 1024;
		}
		return value;
	}

	/**
	 * Retrieve x, y, z 10 bit data in 6 bytes.
	 * 
	 * @param i2c
	 *            Helper class.
	 * @param handle
	 *            I2C file handle.
	 * @param addr
	 *            Address.
	 * @return Map of Integers keyed by x, y, z.
	 */
	public Map<String, Integer> read(final I2c i2c, final i2c_handle handle, final short addr) {
		// Read all 6 registers at once
		final Pointer data = i2c.readArray(handle, addr, (short) 0x32, 6);
		final Map<String, Integer> map = new HashMap<>();
		map.put("x", bytesToInt(data.getByte(0), data.getByte(1)));
		map.put("y", bytesToInt(data.getByte(2), data.getByte(3)));
		map.put("z", bytesToInt(data.getByte(4), data.getByte(5)));
		return map;
	}

	/**
	 * Main program.
	 * 
	 * @param args
	 *            Parameters passed.
	 * @throws InterruptedException
	 *             Possible exception.
	 */
	public static void main(String args[]) throws InterruptedException {
		final I2c i2c = new I2c();
		String device = "/dev/i2c-0";
		short address = 0x53; // 0x53
		// See if there are args to parse
		if (args.length > 0) {
			// I2C device name (default '/dev/i2c-0')
			device = args[0];
			// MPU-6050 address (default 0x53)
			address = (short) Integer.parseInt(args[1], 16);
		}
		// Use to debug if JNA cannot find shared library
		System.setProperty("jna.debug_load", "false");
		System.setProperty("jna.debug_load.jna", "false");
		final i2c_handle handle = i2c.open(device);
		final Adxl345 app = new Adxl345();
		// Check device ID
		if (i2c.readReg(handle, address, (short) 0x00) == 0xe5) {
			// Enable the accelerometer
			i2c.writeReg(handle, address, (short) 0x2d, (short) 0x08);
			// +/- 2g
			app.setRange(i2c, handle, address, (short) 0x00);
			// 100 Hz
			app.setDataRate(i2c, handle, address, (short) 0x0a);
			System.out.println(String.format("Range = %d, data rate = %d", app.getRange(i2c, handle, address),
					app.getDataRate(i2c, handle, address)));
			for (int i = 0; i < 100; i++) {
				final Map<String, Integer> data = app.read(i2c, handle, address);
				System.out.println(
						String.format("x: %04d, y: %04d, z: %04d", data.get("x"), data.get("y"), data.get("z")));
				TimeUnit.MILLISECONDS.sleep(500);
			}
		} else {
			System.out.println("Not ADXL345?");
		}
		i2c.close(handle);
	}
}

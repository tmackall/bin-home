#!/usr/bin/python
# --------------------------------------
# This script reads data from a
# MCP3008 ADC device using the SPI bus.
#
# Author : Matt Hawkins
# Date   : 13/10/2013
#
# http://www.raspberrypi-spy.co.uk/
#
# --------------------------------------

import spidev


def convert_volts(data, places):
    '''
    Function to convert data to voltage level,
    rounded to specified number of decimal places.
    '''
    volts = (data * 3.3) / 1023.0
    volts = round(volts, places)
    return volts


def convert_to_temp(data, places):
    '''
    function: convert_to_temp - converts from voltage to degrees Celcius
    TMP36 data, rounded to specified number of decimal places.
    '''

    # ADC Value
    # (approx)  Temp  Volts
    #    0      -50    0.00
    #   78      -25    0.25
    #  155        0    0.50
    #  233       25    0.75
    #  310       50    1.00
    #  388       75    1.25
    #  465      100    1.50
    #  543      125    1.75
    #  620      150    2.00
    #  698      175    2.25
    #  775      200    2.50
    #  853      225    2.75
    #  930      250    3.00
    # 1008      275    3.25
    # 1023      280    3.30

    # adjusting this temporarily
    temp = ((data * 330.0)/1023)-46.0
    return temp


def convert_c_to_f(temp_c_in):
    '''
    function: convert_c_to_f - takes deg C and converts this to Farenheit
    '''
    return (temp_c_in * 9/5) + 32


class SensorTemp():
    '''
    class: sensorTemp() - used to read adc via spi bus.
    '''
    def __init__(self, channel=0):
        # Open SPI bus
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.channel = channel

    def get(self, farenheit_flag=True):
        '''
        function: temp_f_get() - function to get temp in
        '''
        temp_ret = 0xFF
        temp_level = self.read_channel()
        temp_ret = convert_to_temp(temp_level, 2)
        if farenheit_flag is True:
            temp_ret = convert_c_to_f(temp_ret)

        return temp_ret

    def read_channel(self):
        '''
        Function to read SPI data from MCP3008 chip
        Channel must be an integer 0-7
        '''
        adc = self.spi.xfer2([1, (8+self.channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

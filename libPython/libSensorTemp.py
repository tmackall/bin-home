#!/usr/bin/python
#--------------------------------------
# This script reads data from a
# MCP3008 ADC device using the SPI bus.
#
# Author : Matt Hawkins
# Date   : 13/10/2013
#
# http://www.raspberrypi-spy.co.uk/
#
#--------------------------------------

import spidev
import time
import os

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

def read_channel(channel):
    '''
    Function to read SPI data from MCP3008 chip
    Channel must be an integer 0-7
    '''
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def convert_volts(data, places):
    '''
    Function to convert data to voltage level,
    rounded to specified number of decimal places.
    '''
    volts = (data * 3.3) / 1023
    volts = round(volts,places)
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

    #temp = ((data * 330)/1023)-50
    # adjusting this temporarily
    temp = ((data * 330)/1023)-45
    temp = round(temp, places)
    return temp

def convert_c_to_f(temp_c_in):
    '''
    function: convert_c_to_f - takes deg C and converts this to Farenheit
    '''
    return (temp_c_in * 9/5) + 32




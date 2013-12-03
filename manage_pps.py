#!/usr/bin/env python2.7
"""
module: manage_pps
"""
import logging
from optparse import OptionParser
from pysnmp.proto.rfc1902 import Integer

# local import
from libPython.lib_pps import PPS, house_pps
from libPython.libSNMP import setPortValue
from libPython.lib_snmp import SNMP


LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}


def process_input():
    """
    function: process_input - handles the command-line input
    """

    ret_dict = {}

    # define input parameters
    parser = OptionParser()
    parser.add_option('-e', help='Email address to send warnings',
        dest='em', default='mackall.house@gmail.com')
    parser.add_option('-l', help='Logging Level (e.g. info,warning,debug)',
        default='error', dest='ll')
    parser.add_option('-p', help='Port Number (e.g. 1-16)',
        default=0, dest='inPort')
    parser.add_option('-v', help='Value (e.g. 1=on, 0=off)',
        dest='inValue', default=3)
    parser.add_option('-c', help='Command (e.g. get, set etc)',
        default='get')

    # read input values
    (options, args) = parser.parse_args()

    # process logging
    loggingLevel = LOGGING_LEVELS.get(options.ll, logging.NOTSET)
    logging.basicConfig(format='%(levelname)s - %(message)s',\
        level=loggingLevel)

    # process input port
    ret_dict[port] = int(options.inPort)
    if (port < gPortMin) or (port > gPortMax):
        logging.error('Port - incorrect port: %s', port)
        return(2, ret_dict)

    # process input value (on/off)
    ret_dict[value] = int(options.inValue)
    if value < 0 or value > 1:
        logging.error('Value - incorrect val: %s', value)
        return(3, ret_dict)

    # process person to email
    ret_dict[whereToEmail] = options.em
    logging.debug('Email address input: %s', whereToEmail)

    return(0, ret_dict)


def main():
    """
    function: main - driver for managing the PPSes
    """

    logging.basicConfig(format='%(levelname)s - %(message)s',  \
                    level=logging.WARN)

    #setPortValue(5, 1)
    #snmp = SNMP('192.168.1.99')
    #in_value = 1
    #oid_value = ((1, 3, 6, 1, 4, 1, 20677, 1, 5, 2, 6, 0),
    #          Integer(in_value))
    #snmp.set_value(oid_value)
    mackall_house = house_pps()
    #status, name_values = mackall_house.get_name_values()
    status = mackall_house.set_port('Volume Control Power', 1)
    if status != 0:
        print 'not found'
        return(1)
    status, state = mackall_house.get_port_status('Volume Control Power')
    if status == 0:
        print state
    else:
        print 'not found'
    return(0)
    test = PPS('192.168.1.99')
    print test.get_pps_oids()
    return(1)
    test = PPS('192.168.1.99')
    for i in xrange(8):
        print test.get_port_status(i)
        print test.get_device_name(i)
    test = PPS('192.168.1.98')
    for i in xrange(8):
        print test.get_port_status(i)


    return(0)

if __name__ == "__main__":
    STATUS = main()
    exit(STATUS)

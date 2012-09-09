#!/usr/bin/env python2.7
"""
module: lib_pps - manages programmable power supplies via SNMP
"""
from pysnmp.proto.rfc1902 import Integer
import logging
import time

from libPython.lib_snmp import SNMP


class PPS (SNMP):
    """
    class: PPS  - abstraction layer for single programmable power supplies
    """
    on_off_state_map = {1: 1, 0: 2}  # 1=on,  2=off

    def __init__(self, ip_addr, num_ports=8, port_min=1, port_max=8):
        """
        function: __init__ - initalizes IP address for SNMP, also
            creates port boundaries
        """
        self.ports = num_ports
        self.ip_addr = ip_addr
        self.port_min = port_min
        self.port_max = port_max
        SNMP.__init__(self, self.ip_addr)

    def set_port_value(self, in_port, in_value):
        """
        function: set_port_value - sets the port on/off value for the PPS
        """
        logging.debug('set_port_value in_port: %s, in_value:%s', in_port,
            in_value)
        val = 2  # default to off
        if in_port < self.port_min or in_port > self.port_max:
            return 2
        if (in_value == 1 or in_value == '1' or
            in_value == 'on' or in_value == 'ON'):
            val = 1
        in_port += 1  # command port interfaces are off by 1 (1=all on)
        oid_value = ((1, 3, 6, 1, 4, 1, 20677, 1, 5, 2, in_port,  0),
            Integer(val))
        logging.info('oid_value: %s', str(oid_value))
        ret_status = SNMP.set_value(self, oid_value)
        time.sleep(1)
        return ret_status

    def get_port_status(self, in_port):
        """
        function: get_port_status - gets on/off value of the port
        """
        logging.debug('getPortValue in_port: %s', in_port)
        if in_port < self.port_min or in_port > self.port_max:
            return 2, ''
        oid_value = (1, 3, 6, 1, 4, 1, 20677, 1, 5, 3, in_port, 0)
        ret_status, val = SNMP.get_value(self, oid_value)
        if ret_status != 0:
            return ret_status, ''
        return 0, val

    def get_device_name(self, in_port):
        """
        function: get_device_name - returns the text name of the port
        """
        logging.debug('get_device_name in_port: %s', in_port)
        if in_port < self.port_min or in_port > self.port_max:
            return 2
        oid_value = (1, 3, 6, 1, 4, 1, 20677, 1, 5, 1, in_port, 1, 0)
        ret_status, val = SNMP.get_value(self, oid_value)
        return ret_status, val

    def verify_state(self, in_port, in_value):
        """
        function: verify_state - verifies that the port is in the
            requested state
        """
        logging.debug('verify_state in_port: %s in_value: %s',
            in_port, in_value)
        loop_cnt = 0
        while loop_cnt < 3:
            status, value = self.get_port_status(in_port)
            if status != 0:
                return status
            elif value == PPS.on_off_state_map[in_value]:
                return 0
            time.sleep(1)
            loop_cnt += 1
        return 1

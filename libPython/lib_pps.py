#!/usr/bin/env python2.7
"""
module: lib_pps - manages programmable power supplies via SNMP
"""
from pysnmp.proto.rfc1902 import Integer
import logging
import re
import time

from lib_snmp import SNMP



class PPS (SNMP):
    """
    class: PPS  - abstraction layer for single programmable power supplies
    """
    on_off_state_map = {1: 1, 2: 0}  # 1=on,  2=off

    def __init__(self, ip_addr, num_ports=8, port_min=1, port_max=8):
        """
        function: __init__ - initalizes IP address for SNMP, also
            creates port boundaries
        """
        self.ports = num_ports
        self.ip_addr = ip_addr
        self.port_min = port_min
        self.port_max = port_max
        self.snmp = SNMP(self.ip_addr)

    def get_oid_info(self, in_oid):
        """
        function: get_oid_info - gets PPS info for the oid
        """
        logging.debug('get_oid_info in_oid: %s', in_oid)
        ret_status, val = self.snmp.get_value(in_oid)
        if ret_status != 0:
            return ret_status, ''
        return 0, val

    def set_port_value(self, in_port, in_value):
        """
        function: set_port_value - sets the port on/off value for the PPS
        """
        logging.debug('set_port_value in_port: %s, in_value:%s', in_port,
            in_value)
        if in_port < self.port_min or in_port > self.port_max:
            logging.debug('Port is out of range: %s', in_port)
            return 2
        in_port += 1  # command port interfaces are off by 1 (1=all on)
        oid_value = ((1, 3, 6, 1, 4, 1, 20677, 1, 5, 2, in_port, 0),
            Integer(in_value))
        logging.info('oid_value: %s', str(oid_value))
        status = self.snmp.set_value(oid_value)
        time.sleep(1)
        return status

    def get_port_status(self, in_port):
        """
        function: get_port_status - gets on/off value of the port
        """
        if in_port < self.port_min or in_port > self.port_max:
            logging.debug('Port is out of range: %s', in_port)
            return 2, ''
        logging.debug('get_port_status in_port: %s', in_port)
        oid_value = (1, 3, 6, 1, 4, 1, 20677, 1, 5, 3, in_port, 0)
        status, state = self.get_oid_info(oid_value)
        #return status, PPS.on_off_state_map[int(state)]
        return status, state

    def get_device_name(self, in_port):
        """
        function: get_device_name - returns the text name of the port
        """
        logging.debug('get_device_name in_port: %s', in_port)
        if in_port < self.port_min or in_port > self.port_max:
            logging.debug('Port is out of range: %s', in_port)
            return 2, ''
        oid_value = (1, 3, 6, 1, 4, 1, 20677, 1, 5, 1, in_port, 1, 0)
        ret_status, val = self.snmp.get_value(oid_value)
        return ret_status, str(val)

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

    def get_pps_oids(self):
        """
        function: get_pps_oids - gets all the oids of the pps
        """
        logging.debug('get_pps_oids')
        ret_status, val = self.snmp.walk(self)
        if ret_status != 0:
            return ret_status, ''
        return 0, val


class house_pps(object):
    """
    class: mackall_pps - class to manage house PPS units
    """
    # house global vars
    pps_port_map = {}

    def __init__(self, num_ports=16, ip_list=['192.168.1.99',
        '192.168.1.98']):
        """
        function: __init__ - get the port names and the initial condition
            of them. Assert if these cannot be read.
        """
        logging.debug('enter __init__')
        pps_handle = []
        for ip in ip_list:
            pps_handle.append(PPS(ip))
        tot_ports = 0
        # initialize port mapping to IP addr and to port names
        for j in xrange(len(pps_handle)):
            # assumption is that PPS have same # ports
            pps_port_id = 0 # used for tracking ports per PPS
            for i in xrange(1, num_ports/len(ip_list)+1):
                tot_ports += 1  # total ports
                pps_port_id += 1  # pps port ID
                value = pps_handle[j].get_device_name(i)
                house_pps.pps_port_map[tot_ports] = {'name': value[1],
                    'state' : 'NA', 'handle': pps_handle[j],
                    'port' : pps_port_id}

    def get_name_values(self):
        ret_list = {}
        for i in xrange(1, len(house_pps.pps_port_map)+1):
            pm_ref = house_pps.pps_port_map[i]
            status, pm_ref['state'] = (
                pm_ref['handle'].get_port_status(pm_ref['port']))
            if status != 0:
                logging.error('get_port_status failed: %s', status)
            ret_list[pm_ref['name']] = pm_ref['state']

        return 0, ret_list

    def get_port_status(self, in_port_name):
        """
        function: get_port_status - given a name string of the port
            the function returns on or off (0 = off, 1 = on).
            return -1 if not found
        """
        ret_list = {}
        for i in xrange(1, len(house_pps.pps_port_map)+1):
            pm_ref = house_pps.pps_port_map[i]
            match = re.search(r'^%s$' % in_port_name, pm_ref['name'])
            if match:
                logging.debug('Handle: %s', pm_ref['handle'])
                status, pm_ref['state'] = (
                    pm_ref['handle'].get_port_status(pm_ref['port']))
                if status != 0:
                    logging.error('get_port_status failed: %s', status)
                    return status, ''
                return 0, pm_ref['state']

        return -1, ""

    def reboot_ports(self):
        """
        function: reboot_ports - given a list of ports,
            reboots the ports
        """

    def set_ports(self):
        """
        function: set_ports - given a list of ports,
            sets the ports to value
        """

    def set_port(self, in_port_name, in_value):
        """
        function: set_port - given a port ID, set the value
            value: 1=on, 2=off, 3=reboot
        """
        ret_list = {}
        for i in xrange(1, len(house_pps.pps_port_map)+1):
            pm_ref = house_pps.pps_port_map[i]
            match = re.search(r'^%s$' % in_port_name, pm_ref['name'])
            if match:
                logging.debug('Handle: %s', pm_ref['handle'])
                status = (
                    pm_ref['handle'].set_port_value(pm_ref['port'],
                        in_value))
                if status != 0:
                    logging.error('set_port_value failed: %s', status)
                    return status
                return status

        return -1

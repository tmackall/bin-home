#!/usr/bin/env python2.7
"""
Library to house Python SNMP Class
"""
from pysnmp.entity.rfc3413.oneliner import cmdgen
import logging


class SNMP(object):
    """
    class: SNMP - abstraction of the Python SNMP class
    """

    def __init__(self, ip_addr):
        """
        function: init - creates snmp instance for given IP
        """
        self.ip_addr = ip_addr
        self.transport = cmdgen.UdpTransportTarget((self.ip_addr, 161))
        self.generator = cmdgen.CommandGenerator()

    def get_value(self, in_oid):
        """
        function: get_value - gets port values from a given OID
        """
        logging.debug('get_value in_oid:%s', str(in_oid))
        community = 'public'
        comm_data = cmdgen.CommunityData('server', community, 1)
        res = (error_indication, error_status, _error_index, vsar_binds) =\
            self.generator.getCmd(comm_data, self.transport,
            in_oid)

        if not error_indication is None or error_status is True:
            logging.error('Status of getCmd: %s', str(res))
            return 1, ''
        else:
            logging.info(vsar_binds)
        return 0, vsar_binds[0][1]

    def walk(self):
        """
        function: walk - all oid values
        """
        logging.debug('walk')
        community = 'public'
        comm_data = cmdgen.CommunityData('server', community, 1)
        res = (error_indication, error_status, _error_index, vsar_binds) =\
            self.generator.nextCmd(comm_data, self.transport, 
            '1.3.6.1.4.1.20677.1')

        if not error_indication is None or error_status is True:
            logging.error('Status of getNext: %s', str(res))
            return 1, ''
        else:
            logging.info(vsar_binds)
        return 0, vsar_binds

    def set_value(self, in_oid_value):
        """
        function: set_value - sets the value for a given OID
        """
        logging.debug('set_value in_oid_value:%s', str(in_oid_value))
        community = 'private'
        comm_data = cmdgen.CommunityData('server', community, 1)
        res = (error_indication, error_status, _error_index, vsar_binds) =\
            self.generator.setCmd(comm_data, self.transport, in_oid_value)
        if not error_indication is None or error_status is True:
            logging.error('Status of setCmd: %s', str(res))
            return 1
        else:
            logging.info('%s', vsar_binds)
        return 0


    def set_value(self, in_oid_value):
        """
        function: set_value - sets the value for a given OID
        """
        logging.debug('set_value in_oid_value:%s', str(in_oid_value))
        community = 'private'
        comm_data = cmdgen.CommunityData('server', community, 1)
        res = (error_indication, error_status, _error_index, vsar_binds) =\
            self.generator.setCmd(comm_data, self.transport, in_oid_value)
        if not error_indication is None or error_status is True:
            logging.error('Status of setCmd: %s', str(res))
            return 1
        else:
            logging.info('%s', vsar_binds)
        return 0

    def set_value(self, in_oid_value):
        """
        function: set_value - sets the value for a given OID
        """
        logging.debug('set_value in_oid_value:%s', str(in_oid_value))
        community = 'private'
        comm_data = cmdgen.CommunityData('server', community, 1)
        res = (error_indication, error_status, _error_index, vsar_binds) =\
            self.generator.setCmd(comm_data, self.transport, in_oid_value)
        if not error_indication is None or error_status is True:
            logging.error('Status of setCmd: %s', str(res))
            return 1
        else:
            logging.info('%s', vsar_binds)
        return 0

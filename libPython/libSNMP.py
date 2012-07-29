#!/usr/bin/env python2.7
from datetime import datetime as dt
import logging
from struct import pack, unpack
import os, sys
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1902 import Integer, IpAddress, OctetString
import random
import socket
import time

ip='192.168.1.99'
transport = cmdgen.UdpTransportTarget((ip, 161))
generator = cmdgen.CommandGenerator()
gPortMin=1
gPortMax=8
gExpectedStateMap={1:1,0:2} # 1=on, 2=off
    
def getValue (inOID):
    logging.debug('getValue inOID:%s' % str(inOID))
    community='public'
    comm_data = cmdgen.CommunityData('server', community, 1) 
    myCmd = getattr(generator, 'getCmd')
    #res = (errorIndication, errorStatus, errorIndex, varBinds)\
    #    = myCmd(comm_data, transport, inOID)
    res = (errorIndication, errorStatus, errorIndex, varBinds)=\
        cmdgen.CommandGenerator().getCmd(comm_data, transport, inOID)
    
    if not errorIndication is None  or errorStatus is True:
        logging.error("Error: %s %s %s %s" % res)
    else:
        logging.info( varBinds)
    return 0,varBinds[0][1]
    
def setValue (inOIDValue):
    logging.debug('setValue inOIDValue:%s' % str(inOIDValue))
    community='private'
    comm_data = cmdgen.CommunityData('server', community, 1) # 1 means version SNMP v2c
    res = (errorIndication, errorStatus, errorIndex, varBinds)=\
        cmdgen.CommandGenerator().setCmd(comm_data, transport, inOIDValue)
    if not errorIndication is None  or errorStatus is True:
        logging.Error( "Error: %s %s %s %s" % res)
    else:
        logging.info( "%s" % varBinds)
    return 0

def setPortValue (inPort, inValue):
    logging.debug('setPortValue inPort: %s, inValue:%s' % (inPort,inValue))
    val=2 # default to off
    if inPort < gPortMin or inPort > gPortMax:
        return 2
    if inValue == 1 or inValue == '1' or inValue == 'on' or inValue == 'ON':
        val=1
    inPort+=1 # command port interfaces are off by 1 (1=all on)
    oidValue=((1,3,6,1,4,1,20677,1,5,2,inPort,0),Integer(val))
    logging.info('oidValue: %s' % str(oidValue))
    setValue(oidValue)
    return 0

def getPortStatus (inPort):
    logging.debug('getPortValue inPort: %s' % inPort)
    if inPort < gPortMin or inPort > gPortMax:
        return 2
    oidValue=(1,3,6,1,4,1,20677,1,5,3,inPort,0)
    retStatus,val=getValue(oidValue)
    return 0,val

def getDeviceName (inPort):
    logging.debug('getDeviceName inPort: %s' % inPort)
    if inPort < gPortMin or inPort > gPortMax:
        return 2
    oidValue=(1,3,6,1,4,1,20677,1,5,1,inPort,1,0)
    retStatus,val=getValue(oidValue)
    return 0,val

def verifyState (inPort, inValue):
    logging.debug('verifyState inPort: %s inValue: %s' % (inPort,inValue))
    for i in range(1,3):
        status,value=getPortStatus(inPort)
        if status != 0:
            return status
        elif value == gExpectedStateMap[inValue]:
            return 0
        time.sleep(1)
    return 1


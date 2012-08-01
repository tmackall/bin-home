#!/usr/bin/env python2.7
from optparse import OptionParser
from libPython.libAVR import *

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}

def Main():
    # define input parameters
    parser = OptionParser()
    parser.add_option('-e', help='Email address to send warnings',
        dest='em',default='tmackall@qualcomm.com')
    parser.add_option('-l', help='Logging Level (e.g. info,warning,debug)',
        default='error',dest='ll')
    parser.add_option('-p', help='Port Number (e.g. 1-8)',
        default=9,dest='inPort')
    parser.add_option('-v', help='Value (e.g. 1=on, 0=off)',
        dest='inValue', default=3)

    # read input values
    (options, args) = parser.parse_args()

    # process logging
    loggingLevel = LOGGING_LEVELS.get(options.ll,logging.NOTSET)
    logging.basicConfig(format='%(levelname)s - %(message)s',\
        level=loggingLevel)

    # process input port
    port=int(options.inPort)
    status,state,source,vol=getZone2Status()
    if status == 0:
        logging.debug('State:%s, Source:%s, Volume:%s' %\
            (state,source,vol))
        status,db=convertVolToDB(vol)
        if status==0:
            logging.info('Vol(DB): %s' % db)
    else:
        logging.error('getZone2Status failed')
#    execAVRCmd('ZMOFF')
#    execAVRCmd('SIPANDORA')
#    execAVRCmd('Z2?')
#    execAVRCmd('SIIRADIO')
    execAVRCmd('ZM?')
    execAVRCmd('NSA')
#    execAVRCmd('SI?')


if __name__ == "__main__":
  Main()
  exit (0)

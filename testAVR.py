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
        dest='em',default='mackall.house@gmail.com')
    parser.add_option('-l', help='Logging Level (e.g. info,warning,debug)',
        default='error',dest='ll')

    # read input values
    (options, args) = parser.parse_args()

    # process logging
    loggingLevel = LOGGING_LEVELS.get(options.ll,logging.NOTSET)
    logging.basicConfig(format='%(levelname)s - %(message)s',\
        level=loggingLevel)
    status=execAVRCmd('Z2?')
    print status
    return(0)
    execAVRCmd('Z2ON')
    time.sleep(3)
    #execAVRCmd('NS9Y')
    time.sleep(1)
    execAVRCmd('NSE1')
    time.sleep(1)
    execAVRCmd('NSE1')
    time.sleep(1)
    execAVRCmd('NSE')
    time.sleep(1)
    execAVRCmd('Z2?')
    exit(1)
    time.sleep(1)
    execAVRCmd('Z2?')
    execAVRCmd('ZMOFF')
    time.sleep(1)
    execAVRCmd('NSA')
    exit(0)
    # process input port
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

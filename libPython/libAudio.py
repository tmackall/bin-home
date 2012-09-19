from libAVR import *
from libSNMP import getPortStatus,setPortValue
import logging
from subprocess import call
import time

gAudioCommands={1:'On', 2:'Off', 3:'Reboot'}
INFO_TYPE=[ (0,'INFO'), (1,'ERROR'),(2,'WARNING')]
gVolumeControlPort=5

# reset off the volume controls in the house
def resetVC():
    retStatus=0
    # turn power off
    retStatus=setPortValue(gVolumeControlPort,0)
    if 0 != retStatus:
        logging.error('setPortValue failed: %s' % retStatus)
        retStatus=1
    # turn power on
    retStatus=setPortValue(gVolumeControlPort,1)
    if 0 != retStatus:
        logging.error('setPortValue failed: %s' % retStatus)
        retStatus=1
    return retStatus

def hwAudio(avrPPS, ampPPS, avrIP, command):
    execCmd = command #used to handle command = 3(reboot)
    retStatus = 0
    # get the AVR port status
    status, avState = getPortStatus(avrPPS)
    if status != 0:
        logging.error('getPortStatus returned: %s', status)
    logging.debug ('AVR Current State: %s', gAudioCommands[avState])
    # get the knoll port status
    status,ampState=getPortStatus (ampPPS)
    if status !=0:
        logging.error('getPortStatus returned: %s', status)
    logging.debug ('Amp Current State: %s', gAudioCommands[ampState])
    logging.debug ('Command to exectute: %s', gAudioCommands[command])
    logging.debug ( '%s %s %s' % (str(ampState),str(avState),str(command)))


    #
    # see if the AMP and receiver are already in the requested state
    # return immediately if so unless we are rebooting
    if avState != command or ampState != command or command == 3:

        #
        # Reboot - turn off
        if command == 3:
            execCmd=0 # set to turn off
            logging.info ('processing force off')
        #
        # turn on/off AV receiver
        retStatus=setPortValue(avrPPS, execCmd)
        if 0 != retStatus:
            logging.warning('setPortValue failed: %s' % retStatus)
        #
        # turn on/off Knoll amp
        retStatus=setPortValue(ampPPS, execCmd)
        if 0 != retStatus:
            logging.warning('setPortValue failed: %s' % retStatus)

        # reset the Volume controls if turning the system off
        if gAudioCommands[command] == 'Off':
            resetVC()
        #
        # Reboot - turn on after waiting
        if command == 3:
            logging.info('Reboot- turning on now')
            execCmd = 1 # 'on' command
            #time.sleep(45)
            time.sleep(45)
            #
            # turn on/off AVR receiver
            retStatus=setPortValue(avrPPS, execCmd)
            if 0 != retStatus:
                logging.error('setPortValue failed: %s' % retStatus)
            #
            # turn on/off Knoll amp
            retStatus=setPortValue(ampPPS, execCmd)
            if 0 != retStatus:
                logging.error('setPortValue failed: %s' % retStatus)
    else: #return immediately since it is already in reqeusted state
        # reset the Volume controls if turning the system off
        if gAudioCommands[command] == 'Off':
            resetVC()
        logging.info ('Already in the same state')
        return retStatus

    #
    # system is turned on, so we need to wait
    if command == 1 or command ==3:
        logging.info ('Wait for receiver to come back up')
        #
        # ping the AV server until it responds or times out
        iterations=6
        maxTime=60
        cnt=iterations
        while True:
            shellCommand =  'ping -c 1  ' + avrIP
            retStatus = call(shellCommand, shell=True)
            if retStatus == 0:
                break
            time.sleep(maxTime/iterations)
            cnt -= 1
            if cnt  == 0:
                retStatus=127
                logging.error ('Timeout waiting for AV receiver to come up: %s' % retStatus)
                break
        if retStatus != 0:
            logging.error('Ping timeout on the AVR')
            return retStatus

        #
        # turn the main zone off
        retStatus,retOutput=execAVRCmd('ZMOFF')
        logging.info ('Turning main zone off')
        if retStatus != 0:
            logging.warning('ZMOFF failed: %s ' % retStatus)

        #
        # turn the volume down for Zone 2
        retStatus,retOutput=execAVRCmd('Z230')
        logging.info ('Setting Zone 2 volume.')
        if retStatus != 0:
            logging.warning('Volume set failed')

        #
        # turn on the knoll amp
#        logging.info ('Turning on the knoll amp.')
#        retStatus=setPortValue(ampPPS, execCmd)
#        if 0 != retStatus:
#            logging.warning('setPortValue failed: %s' % retStatus)
    else:
        #
        # for off, delay 1 min
        logging.info ('Sleeping for 1 min on off')
        time.sleep(30)
        logging.debug ('Done Sleeping')
    return retStatus



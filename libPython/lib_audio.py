#!/usr/bin/env python2.7
"""
Library for Django Audio Menu
"""
from libAVR import *
from lib_pps import house_pps
import logging
from subprocess import call
import time


class LIB_AUDIO(object):
    """
    class LIB_AUDIO: class to handle Django Audio requests
    """
    audio_commands = {1: 'On', 2: 'Off', 3: 'Reboot', 'On': 1, 'Off': 2,
            'Reboot': 3, '1': 'On', '2': 'Off', '3': 'Reboot'}
    avr = 'Denon 1912'
    amp = 'Knoll Amp'
    vol_control = 'Volume Control Power'

    def __init__(self):
        self.pps = house_pps()
        self.cmd = LIB_AUDIO.audio_commands[2]

    # reset off the volume controls in the house
    def reset_vc(self):
        ret_status = 0
        # turn power off
        ret_status = self.pps.set_port(LIB_AUDIO.vol_control, 3)
        if 0 != ret_status:
            logging.error('set_port failed: %s', ret_status)
        return ret_status

    def get_state(self):
        '''
        function: get_state - gets the state of the AVR and AMP and
        returns On or Off
        '''
        # get AVR state
        status, avr_state = self.pps.get_port_status(LIB_AUDIO.avr)
        if 0 != status:
            logging.warning('get_port_status failed: %s', status)
            return status

        # get AMP state
        status, amp_state = self.pps.get_port_status(LIB_AUDIO.amp)
        if 0 != status:
            logging.warning('get_port_status failed: %s', status)
            return status

        print 'States: %s %s' % (avr_state, amp_state)
        if amp_state != avr_state:
            return status, 'Off'

        return status, LIB_AUDIO.audio_commands[avr_state]


    def hw_audio(self):
        exec_cmd = LIB_AUDIO.audio_commands[self.cmd] #used to handle command = 3(reboot)
        print 'exec cmd: %s' %  exec_cmd
        ret_status = 0
        #
        # turn on/off AV receiver
        ret_status = self.pps.set_port(LIB_AUDIO.avr, exec_cmd)
        if 0 != ret_status:
            logging.warning('set_port failed: %s', ret_status)
        #
        # turn on/off Knoll amp
        ret_status = self.pps.set_port(LIB_AUDIO.amp, exec_cmd)
        if 0 != ret_status:
            logging.warning('set_port failed: %s', ret_status)

        # reset the Volume controls if turning the system off
        if exec_cmd == 2:
            ret_status = self.pps.set_port(LIB_AUDIO.vol_control, 3)
            if 0 != ret_status:
                logging.error('volume control reset failed: %s',
                        ret_status)

        #
        # system is turned on, so we need to wait
        if exec_cmd == 1 or exec_cmd ==3:
            logging.info ('Wait for receiver to come back up')
            #
            # ping the AV server until it responds or times out
            iterations = 6
            max_time = 60
            cnt = iterations
            while True:
                shell_command =  'ping -c 1 avr '
                ret_status = call(shell_command, shell=True)
                if ret_status == 0:
                    break
                time.sleep(max_time/iterations)
                cnt -= 1
                if cnt  == 0:
                    ret_status = 127
                    logging.error('Timeout waiting for AV receiver'
                        'to come up: %s', ret_status)
                    break
            if ret_status != 0:
                logging.error('Ping timeout on the AVR')
                return ret_status

            #
            # turn the main zone off
            ret_status, retOutput = execAVRCmd('ZMOFF')
            logging.info('Turning main zone off')
            if ret_status != 0:
                logging.warning('ZMOFF failed: %s ', ret_status)

            #
            # turn the volume down for Zone 2
            ret_status, retOutput = execAVRCmd('Z230')
            logging.info('Setting Zone 2 volume.')
            if ret_status != 0:
                logging.warning('Volume set failed')

        else:
            #
            # for off, delay 1 min
            logging.info ('Sleeping for 1 min on off')
            time.sleep(30)
            logging.debug ('Done Sleeping')
        return ret_status



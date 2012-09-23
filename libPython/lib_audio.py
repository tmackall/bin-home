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

    def hw_audio(self):
        exec_cmd = LIB_AUDIO.audio_commands[self.cmd] #used to handle command = 3(reboot)
        print 'exec cmd: %s' %  exec_cmd
        ret_status = 0
        # get the AVR port status
        status, av_state = self.pps.get_port_status(LIB_AUDIO.avr)
        if status != 0:
            logging.error('self.pps.get_port_status returned: %s', status)
        logging.debug('AVR Current State: %s',
                LIB_AUDIO.audio_commands[av_state])
        # get the knoll port status
        status, amp_state = self.pps.get_port_status(LIB_AUDIO.amp)
        if status !=0:
            logging.error('self.pps.get_port_status returned: %s', status)
        logging.debug('Amp Current State: %s',
                LIB_AUDIO.audio_commands[amp_state])
        logging.debug('Command to exectute: %s',
                LIB_AUDIO.audio_commands[self.cmd])
        logging.debug( '%s %s %s', (amp_state, av_state, self.cmd))

        #
        # see if the AMP and receiver are already in the requested state
        # return immediately if so unless we are rebooting
        if av_state != self.cmd or amp_state != self.cmd or self.cmd == 3:

            #
            # Reboot - turn off
            if self.cmd == 3:
                exec_cmd = 0 # set to turn off
                logging.info('processing force off')
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
            if LIB_AUDIO.audio_commands[self.cmd] == 'Off':
                reset_vc()
            #
            # Reboot - turn on after waiting
            if self.cmd == 3:
                logging.info('Reboot- turning on now')
                exec_cmd = 1 # 'on' command
                time.sleep(45)
                #
                # turn on/off AVR receiver
                ret_status = self.pps.set_port(LIB_AUDIO.avr, exec_cmd)
                if 0 != ret_status:
                    logging.error('set_port failed: %s', ret_status)
                #
                # turn on/off Knoll amp
                ret_status=self.pps.set_port(LIB_AUDIO.amp, exec_cmd)
                if 0 != ret_status:
                    logging.error('set_port failed: %s', ret_status)
        else: #return immediately since it is already in reqeusted state
            # reset the Volume controls if turning the system off
            if audio_commands.cmds[self.cmd] == 'Off':
                reset_vc()
            logging.info ('Already in the same state')
            return ret_status

        #
        # system is turned on, so we need to wait
        if self.cmd == 1 or self.cmd ==3:
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



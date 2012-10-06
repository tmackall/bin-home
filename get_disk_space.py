#!/usr/bin/env python2.7
import logging
from libPython.libEmailTools import emailMessage
from optparse import OptionParser
import pexpect
import re
import subprocess

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}


def main():
    ''' main driver
    '''
    # command-line parsing
    parser = OptionParser()
    parser.add_option('--th', dest='threshold', default=45)
    parser.add_option('-p', default='tmackall@qualcomm.com')
    parser.add_option('--fs', dest='fs',
        default='~', help='-fs \'/media-mackall/av,/home/tmackall\'')
    parser.add_option('-l', help='Logging Level',
        default='error', dest='ll')

    (options, _args) = parser.parse_args()

    # process logging
    logging_level = LOGGING_LEVELS.get(options.ll, logging.NOTSET)
    logging.basicConfig(format='%(levelname)s - %(message)s',
        level=logging_level)

    where_to_mail = options.p
    logging.debug('Email address input: %s', where_to_mail)
    warning_percentage = int(options.threshold)
    file_systems = options.fs.split(',')
    # spin the file systems to check
    for file_system in file_systems:
        logging.debug('File system %s', file_system)
        cmd = 'uname -a'
        output = subprocess.check_output(cmd, shell=True)
        match = re.search(r'^Linux ([^\s]+) ', output)
        machine_name = match.group(1)
        cmd1 = 'cd ' + file_system
        cmd2 = 'df .'
        cmd = cmd1 + ";" + cmd2
        output = subprocess.check_output(cmd, shell=True)
        match = re.search(r'(\d+)%[^\/]*(\/.*$)', output)
        if match:
            percent_in_use = int(match.group(1))
            if percent_in_use > warning_percentage:
                subject = ('Server: ' + machine_name + ' Filer: ' +
                    file_system + ' threshold warning!')
                text = ('The current usage of %s is: %i%% '
                    'and the threshold is %i%%'
                    % (file_system, percent_in_use, warning_percentage))
                logging.info(text)
                if where_to_mail != '':
                    emailMessage(where_to_mail, subject, text)
                else:
                    logging.warning('No email address given')
            else:
                logging.info('%i%% is below the threshold of %i%% for %s',
                    percent_in_use, warning_percentage, file_system)
        else:
            text = ('Could not read disk usage from device: %s,' %
                    file_system)
            logging.error(text)
            if where_to_mail != "":
                subject = ('ERROR: issues reading disk for %s' %
                        machine_name)
                emailMessage(where_to_mail, subject, text)

    return(0)

if __name__ == "__main__":
    STATUS = main()
    exit(STATUS)

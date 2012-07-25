#!/usr/bin/env python2.7
import logging
from libEmailTools import emailMessage
from optparse import OptionParser
import pexpect
import re
import subprocess
from sys import exit

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}

def Main():
# command-line parsing
    parser = OptionParser()
    parser.add_option('--threshold','--th',default=45)
    parser.add_option('--personToWarn','-p',
        default='tmackall@qualcomm.com')
    parser.add_option('--fs','--fileSystems', dest='fs',
        default='/media-mackall/av',
        help='--fs \'/media-mackall/av,/home/tmackall\'')
    parser.add_option('-l', '--logging-level', help='Logging Level',
        default=logging.ERROR,dest='ll')

    # process logging
    (options, args) = parser.parse_args()
    loggingLevel = LOGGING_LEVELS.get(options.ll,logging.NOTSET)
    logging.basicConfig(format='%(levelname)s - %(message)s',  \
        level=loggingLevel)


    whereToEmail=options.personToWarn
    warningPercentage=int(options.threshold)
    listFilers=options.fs.split(',')
    # spin the file systems to check
    for i in listFilers:
        logging.debug('File system %s' % i)
        cmd='uname -a'
        output=subprocess.check_output(cmd, shell=True)
        match=re.search(r'^Linux ([^\s]+) ',output)
        machineName=match.group(1)
        cmd1='cd ' + i
        cmd2='df .'
        cmd=cmd1 + ";" + cmd2
        output=subprocess.check_output(cmd, shell=True)
        match=re.search(r'(\d+)%[^\/]*(\/.*$)',output)
        if match:
            percentInUse=int(match.group(1))
            filer=i
            if percentInUse>warningPercentage:
                subject="Server: " + machineName + " Filer: " + \
                    filer + " threshold warning!"
                text='The current usage of %s is: %i%% '\
                    'and the threshold is %i%%'  \
                    % (filer,percentInUse,warningPercentage)
                logging.info(text)
                if whereToEmail != "":
                    emailMessage (whereToEmail, subject, text)
                else:
                    logging.warning('No email address given')
            else:
                logging.info ('%i%% is below the threshold of %i%% for %s' \
                    % (percentInUse,warningPercentage,filer))
    exit(0)

if __name__ == "__main__":
  Main()
  exit (0)


#!/usr/bin/env python2.7
import subprocess
import re
from sys import exit
import pexpect
from libEmailTools import emailMessage
from optparse import OptionParser

def Main():
# command-line parsing
    parser = OptionParser()
    parser.add_option("--threshold",default=45)
    parser.add_option("--personToWarn",default='tmackall@qualcomm.com')
    (options, args) = parser.parse_args()

    whereToEmail=options.personToWarn
    warningPercentage=int(options.threshold)
    listFilers=['/home/media']
    for i in listFilers:
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
                text="The current usage of the filer is: " \
                + str(percentInUse)+'%'
                emailMessage (whereToEmail, subject, text)
            else:
                print str(percentInUse) + ' is  below the threshold of ' + \
                str(warningPercentage)
    exit(0)

if __name__ == "__main__":
  Main()
  exit (0)


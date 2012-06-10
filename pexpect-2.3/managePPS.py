#!/usr/bin/env python

""" This runs a sequence of commands on a remote host using SSH. It runs a
simple system checks such as uptime and free to monitor the state of the remote
host.

./monitor.py [-s server_hostname] [-u username] [-p password]
    -s : hostname of the remote server to login to.
    -u : username to user for login.
    -p : Password to user for login.

Example:
    This will print information about the given host:
        ./monitor.py -s www.example.com -u mylogin -p mypassword

It works like this:
    Login via SSH (This is the hardest part).
    Run and parse 'uptime'.
    Run 'iostat'.
    Run 'vmstat'.
    Run 'netstat'
    Run 'free'.
    Exit the remote host.
"""

import os, sys, time, re, getopt, getpass
import traceback
import pexpect

#
# Some constants.
#
COMMAND_PROMPT = '[#$] ' ### This is way too simple for industrial use -- we will change is ASAP.
TERMINAL_PROMPT = '(?i)terminal type\?'
TERMINAL_TYPE = 'vt100'
# This is the prompt we get if SSH does not have the remote host's public key stored in the cache.
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'

def exit_with_usage():

    print globals()['__doc__']
    os._exit(1)

def main():

    global COMMAND_PROMPT, TERMINAL_PROMPT, TERMINAL_TYPE, SSH_NEWKEY
    #
    # Login via SSH
    #
    child = pexpect.spawn('bash')
    COMMAND_PROMPT='uniQuePrompt#'
    sCommand='export PS1=uniQuePrompt#'
    child.sendline (sCommand)
    i = child.expect([pexpect.TIMEOUT, COMMAND_PROMPT])
    if i == 0: # Timeout
        print 'ERROR: Setting the prompt'
        print child.before, child.after
        print str(child)
        sys.exit (1)
    if i == 1: # In this case SSH does not have the public key cached.
	print "Made it!"

    sCommand2='snmpwalk -Os -c public -v2c pps1 Pulizzi'
    child.sendline (sCommand2)
    i = child.expect([pexpect.TIMEOUT, COMMAND_PROMPT], timeout=5)
    print child.after
#    if i == 0: # In this case SSH does not have the public key cached.
#	print '[sCommand] timeout'
#    if i == 1: # In this case SSH does not have the public key cached.
#	print child.after
    sys.exit(33)
    #
    # Set command prompt to something more unique.
    #
    i = child.expect ([pexpect.TIMEOUT, COMMAND_PROMPT], timeout=10)
    if i == 0:
        print "# Couldn't set sh-style prompt -- trying csh-style."
        child.sendline ("set prompt='[PEXPECT]\$ '")
        i = child.expect ([pexpect.TIMEOUT, COMMAND_PROMPT], timeout=10)
        if i == 0:
            print "Failed to set command prompt using sh or csh style."
            print "Response was:"
            print child.before
            sys.exit (1)

    # Now we should be at the command prompt and ready to run some commands.
    print '---------------------------------------'
    print 'Report of commands run on remote host.'
    print '---------------------------------------'

    # Run uname.
    child.sendline ('uname -a')
    child.expect (COMMAND_PROMPT)
    print child.before
    if 'linux' in child.before.lower():
        LINUX_MODE = 1
    else:
        LINUX_MODE = 0

    # Run and parse 'uptime'.
    child.sendline ('uptime')
    child.expect('up\s+(.*?),\s+([0-9]+) users?,\s+load averages?: ([0-9]+\.[0-9][0-9]),?\s+([0-9]+\.[0-9][0-9]),?\s+([0-9]+\.[0-9][0-9])')
    duration, users, av1, av5, av15 = child.match.groups()
    days = '0'
    hours = '0'
    mins = '0'
    if 'day' in duration:
        child.match = re.search('([0-9]+)\s+day',duration)
        days = str(int(child.match.group(1)))
    if ':' in duration:
        child.match = re.search('([0-9]+):([0-9]+)',duration)
        hours = str(int(child.match.group(1)))
        mins = str(int(child.match.group(2)))
    if 'min' in duration:
        child.match = re.search('([0-9]+)\s+min',duration)
        mins = str(int(child.match.group(1)))
    print
    print 'Uptime: %s days, %s users, %s (1 min), %s (5 min), %s (15 min)' % (
        duration, users, av1, av5, av15)
    child.expect (COMMAND_PROMPT)

    # Run iostat.
    child.sendline ('iostat')
    child.expect (COMMAND_PROMPT)
    print child.before

    # Run vmstat.
    child.sendline ('vmstat')
    child.expect (COMMAND_PROMPT)
    print child.before

    # Run free.
    if LINUX_MODE:
        child.sendline ('free') # Linux systems only.
        child.expect (COMMAND_PROMPT)
        print child.before

    # Run df.
    child.sendline ('df')
    child.expect (COMMAND_PROMPT)
    print child.before
    
    # Run lsof.
    child.sendline ('lsof')
    child.expect (COMMAND_PROMPT)
    print child.before

#    # Run netstat
#    child.sendline ('netstat')
#    child.expect (COMMAND_PROMPT)
#    print child.before

#    # Run MySQL show status.
#    child.sendline ('mysql -p -e "SHOW STATUS;"')
#    child.expect (PASSWORD_PROMPT_MYSQL)
#    child.sendline (password_mysql)
#    child.expect (COMMAND_PROMPT)
#    print
#    print child.before

    # Now exit the remote host.
    child.sendline ('exit')
    index = child.expect([pexpect.EOF, "(?i)there are stopped jobs"])
    if index==1:
        child.sendline("exit")
        child.expect(EOF)

if __name__ == "__main__":

    try:
        main()
    except Exception, e:
        print str(e)
        traceback.print_exc()
        os._exit(1)


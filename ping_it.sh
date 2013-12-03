#!/bin/bash
    # Simple SHELL script for Linux and UNIX system monitoring with
    # ping command
    # -------------------------------------------------------------------------
    # Copyright (c) 2006 nixCraft project <http://www.cyberciti.biz/fb/>
    # This script is licensed under GNU GPL version 2.0 or above
    # -------------------------------------------------------------------------
    # This script is part of nixCraft shell script collection (NSSC)
    # Visit http://bash.cyberciti.biz/ for more information.
    # -------------------------------------------------------------------------
    # Setup email ID below
    # See URL for more info:
    # http://www.cyberciti.biz/tips/simple-linux-and-unix-system-monitoring-with-ping-command-and-scripts.html
    # -------------------------------------------------------------------------
if [ "$#" -lt 1 ]; then
    echo "Please provide a device to ping."
    exit 1
fi
args=("$@")
HOST="${args[0]}"
# add ip / hostname separated by white space
 
# no ping request
COUNT=1
 
# email report when
SUBJECT="Ping failed"
EMAILID="mackall.house@gmail.com"
TEMP_FILE="/tmp/m"
count=$(ping -c $COUNT "$HOST" | grep 'received' | awk -F',' '{ print $2 }' | awk '{ print $1 }')
if [ $count -eq 0 ]; then
# 100% failed
    echo "Host : "$HOST" is down (ping failed) at $(date)" > ${TEMP_FILE}
    echo "Rebooting POE switch" >> ${TEMP_FILE}
    mutt $EMAILID -s "$SUBJECT" < ${TEMP_FILE}
    ~/bin/reboot_3com.sh
    exit 2
fi
exit 0

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
     
    # add ip / hostname separated by white space
    HOSTS="192.168.1.15 192.168.1.18"
     
    # no ping request
    COUNT=1
     
    # email report when
    SUBJECT="Ping failed"
    EMAILID="tmackall@qualcomm.com"
    TEMP_FILE="/tmp/m"
    for myHost in $HOSTS
    do
      count=$(ping -c $COUNT $myHost | grep 'received' | awk -F',' '{ print $2 }' | awk '{ print $1 }')
      if [ $count -eq 0 ]; then
    # 100% failed
        echo "Host : $myHost is down (ping failed) at $(date)" > ${TEMP_FILE}
        echo "Rebooting POE switch" >> ${TEMP_FILE}
        ~/bin/email_msg.py -e $EMAILID -s "$SUBJECT" -m ${TEMP_FILE}
        ~/bin/reboot_3com.sh

      fi
    done

#!/bin/bash
# Test an IP address for validity:
# Usage:
#      valid_ip IP_ADDRESS
#      if [[ $? -eq 0 ]]; then echo good; else echo bad; fi
#   OR
#      if valid_ip IP_ADDRESS; then echo good; else echo bad; fi
#
function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

. /home/tmackall/.bashrc
SERVER=192.168.1.18:8000 
if [[ $# > 0 ]]; then
    SERVER="$1"
    IP=$(echo $1 | sed 's/\(.*\)\:[0-9]\{1,6\}$/\1/')
    valid_ip "$IP"
    if [[ 0 -ne $? ]]; then
        echo "Invalid IP/Port - e.g. 192.168.1.18:8000"
        exit 2
    fi
    echo "$IP"
fi
nohup /home/tmackall/django/mackallHouse/manage.py runserver "$SERVER" > /home/tmackall/django.log 2>&1 &
exit 0



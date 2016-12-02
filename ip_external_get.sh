#!/bin/bash
IP_FILE="/tmp/ip_external.txt"
IP_NOW=$(curl ipecho.net/plain ; echo)
echo $IP_NOW
if [[ ! "$IP_NOW" =~ [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ ]]; then
    email_subject="IP get failure: $IP_NOW"
    echo "$email_subject"
    mutt mackall.tom@gmail.com -s "${email_subject}" < /dev/null
    exit 1
fi
ip_external=$(cat $IP_FILE)
if [[ "$IP_NOW" != "$ip_external" ]]; then
    email_subject="IP:${ip_external} has changed to IP:${IP_NOW}"
    echo $IP_NOW > $IP_FILE
    mutt mackall.tom@gmail.com -s "${email_subject}" < /dev/null
fi

#!/bin/bash
ip_file="/tmp/ip_external.txt"
ip_now=$(curl -s icanhazip.com )
echo $ip_now
ip_external=$(cat $ip_file)
if [[ "$ip_now" != "$ip_external" ]]; then
    email_subject="IP:${ip_external} has changed to IP:${ip_now}"
    echo $ip_now > $ip_file
    mutt mackall.tom@gmail.com -s "${email_subject}" < /dev/null
fi


#!/bin/bash

if [[ $# -lt 1 ]]; then
    echo -e "\n$0 <device> [params]\n"
    exit 2
fi
off=0
on=1
device="$1"
val="$2"
exp_val=1
if [[ $val =~ off ]]; then
    exp_val=0
fi
wemo clear
MAX_TRIES=5
for i in {1..5}; do
    echo $i
    wemo -f switch "$device" "$val"
    on_off=$(wemo status | grep "$device" | awk  '{ print $NF }')
    if [[ $exp_val -eq $on_off ]]; then
        echo "correct state: $on_off"
        exit 0
    fi
    sleep 3
done
exit 1

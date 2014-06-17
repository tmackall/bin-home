#!/bin/bash

if [[ $# -lt 2 ]]; then 
    echo "Usage: $0 <upper limit> <lower limit>"
    exit 1
fi

UL=$1
LL=$2

echo "$UL $LL"


export PATH=~/bin:$PATH
TEMP_STRING=$(curl http://mackall-rp04/sensor_temp/)

TEMP_FMT=$(echo "$TEMP_STRING" | sed 's/.*) *//')
TEMP=$(echo "$TEMP_FMT" | sed 's/ *F//' | sed 's/\([0-9]\+\...\).*/\1/')
echo "$TEMP"
exit
#TEMP=$(echo "$TEMP_FMT" | sed 's/ *F//')
RESULT1=$(echo "$TEMP > $UL" | bc)
RESULT2=$(echo "$TEMP < $LL" | bc)
echo -e "\n${TEMP}F\n"
if [[ $RESULT1 -ne 0 ]] || [[ $RESULT2 -ne 0 ]]; then
    SUBJECT="Warning: house temp is: $TEMP"
    echo "$SUBJECT"
    mutt "mackall.tom@gmail.com" -s "${SUBJECT}" < /dev/null
    /home/tmackall/bin/text_message.sh -n 3032411300 -m "$SUBJECT"
fi

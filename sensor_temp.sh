#!/bin/bash


TEMP_STRING=$(curl --data "test=false" http://mackall-rp04:8000/sensor_temp/)

TEMP_FMT=$(echo "$TEMP_STRING" | sed 's/.*) *//')
TEMP=$(echo "$TEMP_FMT" | sed 's/ *F//')
RESULT1=$(echo "$TEMP > 71.0" | bc)
RESULT2=$(echo "$TEMP < 65.0" | bc)
echo -e "\n${TEMP}F\n"
if [[ $RESULT1 -ne 0 ]] || [[ $RESULT2 -ne 0 ]]; then
    SUBJECT="Warning: house temp is: $TEMP"
    echo "$SUBJECT"
    mutt "mackall.tom@gmail.com" -s "${SUBJECT}" < /dev/null
    text_message.sh -n 3032411300 -m "$SUBJECT"
fi

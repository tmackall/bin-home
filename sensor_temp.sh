#!/bin/bash


pushd /home/tmackall/bin
TEMP_STRING=$(sudo ./sensor_temp.py)
popd

TEMP=$(echo "$TEMP_STRING" | sed 's/.*) *//')
SUBJECT="House temp is: $TEMP"
echo "$SUBJECT"
mutt "mackall.tom@gmail.com" -s "${SUBJECT}" < /dev/null

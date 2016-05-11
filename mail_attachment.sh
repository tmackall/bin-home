#!/bin/bash
# ------------------------------------------------------
#
# script that can be used to send attachments.
#
# ------------------------------------------------------

BODY=""
NUM_ARGS=$#
if [[ $NUM_ARGS -lt 3 ]]; then
    echo -e "\n$0 <subject> <attachment file> <email address> [body]\n"
    exit 2
fi
if [[ $# -eq 4 ]]; then
    BODY="-d $4"
fi

SUBJECT="$1"
ATTACH_FILE="$2"
EMAIL_ADDR="$3"

cmd="mpack -s \"$SUBJECT\" $ATTACH_FILE  $EMAIL_ADDR $BODY"
echo "$cmd"
eval $cmd

exit $?

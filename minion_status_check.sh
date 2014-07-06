#!/bin/bash

FLAG_UP_DOWN=""

usage()
{
cat << EOF
usage: $0 options

This script uses a web app to send a text message.

OPTIONS:
   -h      help
   -u      send up message
   -d      send down message
   -b      send both - up and down status
EOF
}

MESSAGE=""
NUMBER=""
while getopts “hudb” OPTION
do
	case $OPTION in
	h)
	    usage
	    exit 4
	    ;;
	u)
	    FLAG_UP_DOWN=1
	    ;;
	d)
	    FLAG_UP_DOWN=2
	    ;;
	b)
	    FLAG_UP_DOWN=0
	    ;;
	?)
	    usage
	    exit 5
	    ;;
	esac
done

if [[ "$FLAG_UP_DOWN" == "" ]]; then
    usage
    exit 6
fi

#
# minion status - filter out
# --------------------------------------------
STATUS_MINION=$(salt/salt_minion_status.sh)
STATUS_UP=$(echo $STATUS_MINION | sed 's/.*up://')
STATUS_DOWN=$(echo $STATUS_MINION | sed 's/up:.*//' | sed 's/.*down: *//')
FILE_TMP="/tmp/$$.txt"

#
# email? - check on the situation first
# --------------------------------------------
SUBJECT=""
TEXT=""
if [[ $FLAG_UP_DOWN -eq 0 ]]; then
    #
    # both
    SUBJECT="Mackall house minion status"
    TEXT="Minions up: $STATUS_UP"
    TEXT+="\n"
    TEXT+="Minions down: $STATUS_DOWN"
    echo -e "$TEXT" > $FILE_TMP
    mutt mackall.tom@gmail.com -s "$SUBJECT" < $FILE_TMP
    rm -rf $FILE_TMP

elif [[ $FLAG_UP_DOWN -eq 1 ]]; then
    #
    # up
    SUBJECT="Minions up: $STATUS_UP"
    echo -e "$TEXT" > $FILE_TMP
    mutt mackall.tom@gmail.com -s "$SUBJECT" < $FILE_TMP
    rm -rf $FILE_TMP

else
    #
    # down
    SUBJECT="Warning: minions down: $STATUS_DOWN"
    echo -e "$TEXT" > $FILE_TMP
    if [[ ! "$STATUS_DOWN" == "" ]]; then
        mutt mackall.tom@gmail.com -s "$SUBJECT" < $FILE_TMP
    fi
    rm -rf $FILE_TMP
fi
exit 0


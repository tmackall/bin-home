#!/bin/bash

usage()
{
cat << EOF
usage: $0 options

This script uses a web app to send a text message.

OPTIONS:
   -h      help
   -m      message
   -n      number (3032411300)
EOF
}

MESSAGE=""
NUMBER=""
while getopts “hm:n:” OPTION
do
	case $OPTION in
	h)
	    usage
	    exit 4
	    ;;
	m)
	    MESSAGE=$OPTARG
	    ;;
	n)
	    NUMBER=$OPTARG
	    ;;
	?)
	    usage
	    exit
	    ;;
	esac
done

if [[ "$MESSAGE" == "" ]] || [[ "$NUMBER" == "" ]]; then
    usage
    exit 1
fi
curl http://textbelt.com/text -d number=$NUMBER -d "message=$MESSAGE"



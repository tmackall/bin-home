#!/bin/sh
if [ $# -lt 2 ]; then
    echo "$# params passed"
    echo "Usage: rsync.sh <from> <to>"
    echo "Usage: rsync.sh fromdir server:/toDir"
    exit 2
fi
FROM=$1
TO=$2
CMD="rsync -avz  ${FROM} ${TO}"
#CMD="rsync -avz --exclude-from /Users/tmackall/bin/rsyn-exclude-list.txt ${FROM} ${TO}"
echo "$CMD"
$CMD

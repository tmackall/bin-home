#!/bin/sh
if [ $# -lt 2 ]; then
    echo "$# params passed"
    echo "Usage: rsync.sh <from> <to>"
    echo "Usage: rsync.sh fromdir server:/toDir"
    exit 2
fi
FROM=$1
TO=$2
#CMD="rsync -avz  -X ~/bin/rsync_exclude.txt ${FROM} ${TO}"
CMD="rsync -avz --exclude-from /home/tmackall/bin/rsync-exclude.txt ${FROM} ${TO}"
TEMP_FILE=$(mktemp /tmp/XXXX)
echo "${CMD}" > ${TEMP_FILE}
OUTPUT=$(eval "${CMD}")
echo "${OUTPUT}" >> ${TEMP_FILE}
SUBJECT="Home Computer Sync Finished."
mutt tmackall@qti.qualcomm.com -s "${SUBJECT}" < ${TEMP_FILE}
rm ${TEMP_FILE}

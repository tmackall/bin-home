#!/bin/bash
PATH=$PATH:/usr/lib/nagios/plugins
if [[ $# -ne 1 ]]; then
    echo "Usage: #0 <hostname>"
    exit 2
fi

HN="$1"
ADDR_EMAIL="mackall.tom@gmail.com"
SUBJ="Machine \"$HN\" cannot be reached"
NOTE_FILE="/tmp/$HN"
NOTE_DELAY=30

#
# nagios - ping the host
name=$(check_by_ssh -H $HN "hostname")
status=$?

#
# nagios status - non-0 if fails
if [[ $status -ne 0 ]]; then
    #
    # spam logic - only send email every X minutes
    file_test=$(find $NOTE_FILE -amin +${NOTE_DELAY})
    status=$?
    echo "$status \"$file_test\""
    if [[ $status -ne 0 ]] || [[ $file_test != "" ]]; then
        echo "Failed to contact host: $HN"
        mutt $ADDR_EMAIL -s "$SUBJ" < /dev/null
        touch "$NOTE_FILE"
    fi
    exit 3
fi
exit 0

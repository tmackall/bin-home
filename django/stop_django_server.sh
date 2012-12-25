#!/bin/bash
# Stop the Audio Server
#
# keep looking for django servers
while [[ $(ps -eaf | egrep "manage\.py runserver") ]]; do
    # grab the process ID with ps and awk
    OUTPUT=$(ps -eaf | egrep "manage\.py runserver")
    PROCESS_ID=$(echo $OUTPUT | awk '{print $2;}')
    # check for a django process
    if [[ $PROCESS_ID =~ ^[0-9]+$ ]]; then
        # don't take any chances
        kill -9 $PROCESS_ID
        STATUS=$?
        if [[ $STATUS -eq 0 ]]; then
            echo "Killed $PROCESS_ID successfully!"
        else
            echo "Failed to stop: $PROCESS_ID"
        fi
    else
        echo "No process to kill"
        exit 127
    fi
done



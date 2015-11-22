#!/bin/bash
    # -------------------------------------------------------------------------
if [ "$#" -lt 1 ]; then
    echo "Usage $0 <file to copy>"
    exit 1
fi
args=("$@")
FILE_TO_COPY="${args[0]}"


#
# 
scp -i ~/aws.pem "$FILE_TO_COPY" ubuntu@52.27.223.220:
exit 0

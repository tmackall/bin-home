#!/bin/bash

if [[ $# < 1 ]]; then
    echo "Usage: $0 <dir head>"
    exit 1
fi

dir_head=$1
# find 10M+ files
find ${dir_head} -type f -size +10000k -exec ls -lh {} \; | awk '{ print $9 ": " $5 }'

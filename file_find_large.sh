#!/bin/bash

if [[ $# < 2 ]]; then
    echo "Usage: $0 <dir head> <size kilobytes>"
    exit 1
fi

dir_head=$1
size=$2
# find 10M+ files
find ${dir_head} -type f \( ! -name mnt \) -size +${size}k -exec ls -lh {} \; | awk '{ print $9 ": " $5 }'

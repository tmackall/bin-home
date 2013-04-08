#!/bin/bash

script=$0
fs="$1"

if [[ $fs =~ ^\ *$ ]]; then
    echo -e "\n$script failed: $script [file system]\n"
    exit 2
fi


output=$(df $1)
status=$?
if [[ $status -ne 0 ]]; then
    echo -e "\nFile System: $1 is likely invalid\n"
    exit 3
fi

pcent=$(echo $output | sed 's/.* \([0-9]\+\)% .*/\1/') 
echo $pcent
exit 0

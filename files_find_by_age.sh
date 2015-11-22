#!/bin/bash

if [[ $# -lt 2 ]]; then
    echo -e "\nUsage: $0 <base dir> <# days>\n"
    exit 2
fi

BASE_DIR="$1"
DAYS=$2

cnt=0
for i in $(find "$BASE_DIR" -type f -mtime +$((${DAYS} - 1))); do
    ((cnt = $cnt +1))
    rm -rf "$i"
    # delete the dir
    echo -e "$i"
done

echo -e "\n${cnt} dirs deleted\n"
exit 0

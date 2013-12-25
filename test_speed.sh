#!/bin/bash
file_output="/tmp/speedtest.txt"
rm "$file_output"
if [[ $? != 0 ]]; then
    echo "Failed to delete: $file_output"
    exit 1
fi

# execute the broadbad/internet speed test
speedtest > "$file_output"

if [[ $? != 0 ]]; then
    echo "Failed speed test"
    exit 2
fi
DL_SPEED=$(cat $file_output | grep -i "^Download")
UL_SPEED=$(cat $file_output | grep -i "^Upload")
mutt mackall.tom@gmail.com -s "$DL_SPEED, $UL_SPEED" < /dev/null
exit 0

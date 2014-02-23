#!/bin/bash
file_output="/tmp/speedtest.out"
if [[ -e "$file_output" ]]; then
    rm "$file_output"
fi

# execute the broadbad/internet speed test
speedtest-cli > "$file_output" 2>&1

if [[ $? != 0 ]]; then
    echo "Failed speed test"
    exit 2
fi
DL_SPEED=$(cat $file_output | grep -i "^Download")
UL_SPEED=$(cat $file_output | grep -i "^Upload")
PROVIDER=$(cat $file_output | grep "Testing from" | sed 's/Testing from //' | sed 's/\.\.\.//')
mutt mackall.tom@gmail.com -s "$PROVIDER: $DL_SPEED, $UL_SPEED" < "$file_output"
exit 0

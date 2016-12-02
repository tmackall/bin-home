#!/bin/bash
FILE_OUT=$(mktemp)
echo $FILE_OUT

# execute the broadbad/internet speed test
speedtest-cli > "$FILE_OUT" 2>&1
STATUS=$?

echo $(whoami)
if [[ $STATUS != 0 ]]; then
    echo "Failed speed test: $STATUS"
    rm $FILE_OUT
    exit 2
fi
DL_SPEED=$(cat $FILE_OUT | grep -i "^Download")
UL_SPEED=$(cat $FILE_OUT | grep -i "^Upload")
PROVIDER=$(cat $FILE_OUT | grep "Testing from" | sed 's/Testing from //' | sed 's/\.\.\.//')
mutt mackall.tom@gmail.com -s "$PROVIDER: $DL_SPEED, $UL_SPEED" < "$FILE_OUT"
rm $FILE_OUT
exit 0

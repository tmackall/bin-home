#!/bin/bash
# gets the process ID of the Django serverr
#
TEMP_FILE=$(mktemp /tmp/XXXX)
ps -ef | grep "django" | egrep "manage\.py runserver" | awk '{print $2}' | while read line ;
do
    echo -ne "$line " >> $TEMP_FILE
done
echo " " >> $TEMP_FILE
cat $TEMP_FILE
rm $TEMP_FILE



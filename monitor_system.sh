#!/bin/bash
source ~/.bashrc

TEMP_FILE=$(mktemp /tmp/XXXX)

SUBJECT="Home computer system stats"
cat /proc/cpuinfo > ${TEMP_FILE}
df -a >> ${TEMP_FILE}
~/develop/email_msg.py -e tmackall@qualcomm.com -m ${TEMP_FILE} -s "${SUBJECT}"


rm ${TEMP_FILE}

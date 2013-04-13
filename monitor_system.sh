#!/bin/bash

TEMP_FILE=$(mktemp /tmp/XXXX)
host_name=$(hostname)
SUBJECT="${host_name} computer system stats"
echo -e "Uptime info: " >> ${TEMP_FILE}
uptime >> ${TEMP_FILE}
echo -e "\n\nFree info: " >> ${TEMP_FILE}
free >> ${TEMP_FILE}
echo -e "\n\niostat info: " >> ${TEMP_FILE}
iostat >> ${TEMP_FILE}
echo -e "\n\nDisk Usage Info: " >> ${TEMP_FILE}
df -a >> ${TEMP_FILE}
NETSTAT_FILE=$(mktemp /tmp/XXXX)
echo -e "\n\nnetstat -a Info: " >> ${NETSTAT_FILE}
netstat -a >> ${NETSTAT_FILE}
echo -e "\n\npstree Info: " >> ${TEMP_FILE}
pstree >> ${TEMP_FILE}

mutt tmackall@quicinc -a /proc/meminfo -a /proc/cpuinfo -a ${NETSTAT_FILE}  -s "${SUBJECT}" < ${TEMP_FILE} 


rm ${NETSTAT_FILE}
rm ${TEMP_FILE}

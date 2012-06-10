#!/bin/bash 

P4=/pkg/asw/tools/bin/p4
ECHO=/bin/echo

${ECHO} -e "Current ClientSpec is ${P4CLIENT}\n"
CMD="${P4} clients -u ${USER}"
CLIENTLIST=`${CMD}`

ID='1'
for CLIENT in $( ${CMD} | cut -d' ' -f 2 )
do
   ${ECHO} -e "   ${ID}: ${CLIENT}"
   ID=$((ID+1))
done
${ECHO} -e "   0: EXIT\n"

read -p "   Pick a clientspec: " CHOICE

ID='1'
for CLIENT in $( ${CMD} | cut -d' ' -f 2 )
do
   if [[ $CHOICE = $ID ]]
   then export P4CLIENT=${CLIENT}
   fi
   ID=$((ID+1))
done

${ECHO} -e "\nP4CLIENT is set to ${P4CLIENT}"

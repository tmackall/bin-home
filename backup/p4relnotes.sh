#!/bin/bash
#
# p4relnotes.sh
#
# p4 changes -m1 @label1       [say this is 200]
# p4 changes -m1 @label2       [and say this is 250]
# p4 changes //labelview/...@201,@250
# p4 describe <each change in the last command> #

LABEL_1=$1
LABEL_2=$2
LABELVIEW=$3
P4=/pkg/asw/tools/bin/p4
ECHO=/bin/echo
BASENAME=/usr/bin/basename

if [ $# -ne 3 ]
then
    ${ECHO} "Usage: `${BASENAME} $0` label1 label2 labelview"
    exit 65;    # E_WRONGARGS
fi

${ECHO} -e "\nP4CLIENT: ${P4CLIENT}\n"

# p4 changes -m1 @label1       [say this is 200]
CMD="${P4} changes -m1 @${LABEL_1}"
FIRSTCL=`${CMD}`
${ECHO} -e "First Change:\n${CMD}\n${FIRSTCL}\n"
FIRSTCL=`${ECHO} ${FIRSTCL} | cut -d' ' -f 2`  # only want changelist number
FIRSTCL=`expr ${FIRSTCL} + 1`                  # inclusive changes only

# p4 changes -m1 @label2       [and say this is 250]
CMD="${P4} changes -m1 @${LABEL_2}"
LASTCL=`${CMD}`
${ECHO} -e "Last Change:\n${CMD}\n${LASTCL}\n"
LASTCL=`${ECHO} ${LASTCL} | cut -d' ' -f 2`   # only want changelist number

# p4 changes //labelview/...@201,@250
CMD="${P4} changes //${LABELVIEW}/...@${FIRSTCL},@${LASTCL}"
CHANGELISTS=`${CMD}`


# p4 describe <each change in the last command> 
for CHANGE in $( ${CMD} |  cut -d' ' -f 2 ) 
do
   DESC="${P4} describe -s ${CHANGE}"
   ${ECHO} -e "${DESC}\n"
   ${DESC}
done

exit 0

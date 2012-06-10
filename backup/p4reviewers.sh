#!/bin/bash
#
# p4reviewers.sh
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
LABELVIEW='source/qcom/qct/platform/linux/*/main/latest'

if [ $# -ne 2 ]
then
    ${ECHO} "Usage: `${BASENAME} $0` label1 label2"
    exit 65;    # E_WRONGARGS
fi

# p4 changes -m1 @LABEL_1       [say this is 200]
CMD="${P4} changes -m1 @${LABEL_1}"
FIRSTCL=`${CMD}`
FIRSTCL=`${ECHO} ${FIRSTCL} | cut -d' ' -f 2`  # only want changelist number
FIRSTCL=`expr ${FIRSTCL} + 1`                  # inclusive changes only

# p4 changes -m1 @LABEL_2       [and say this is 250]
CMD="${P4} changes -m1 @${LABEL_2}"
LASTCL=`${CMD}`
LASTCL=`${ECHO} ${LASTCL} | cut -d' ' -f 2`   # only want changelist number

# p4 changes //labelview/...@201,@250
CMD="${P4} changes //${LABELVIEW}/...@${FIRSTCL},@${LASTCL}"
CHANGELISTS=`${CMD}`

${ECHO} -e "PEER REVIEW REPORT:\nDiffing @${LABEL_1}(CL:${FIRSTCL}) and @${LABEL_2}(CL:${LASTCL})\n"

# p4 describe <each change in the last command> 
for CHANGE in $( ${CMD} |  cut -d' ' -f 2 ) 
do
   ${ECHO} -e "-----------------------------------------------------------"
   ${P4} describe -s ${CHANGE} | grep -A1 "Change.*by.*on\|Peer Review"
done

${ECHO} -e "-----------------------------------------------------------"

exit 0

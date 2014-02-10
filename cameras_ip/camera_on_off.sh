#!/bin/bash

#==================================================================
#
# Script used to update the cameras.xml file. This is used by the 
# detect_ftp_files.sh script to determine if email should be
# sent for a camera or not.
#
#==================================================================

#
# commmand line arguments 
#------------------------------------------------------------------

usage()
{
cat << EOF
usage: $0 options

This script run the test1 or test2 over a machine.

OPTIONS:
   -h      help
   -a      all camera
   -c      camera list "SS01 SS02" - must supply a value
   -y      camera on
   -n      camera off
EOF
}

CAMERA_ALL_FLAG=1
CAMLERA_LIST=
ON_OFF_FLAG=
while getopts “hc:yn” OPTION
do
	case $OPTION in
	h)
	    usage
	    exit 4
	    ;;
	c)
	    CAMLERA_LIST=$OPTARG
	    CAMERA_ALL_FLAG=0
	    ;;
	y)
	    ON_OFF_FLAG="on"
	    ;;
	n)
	    ON_OFF_FLAG="off"
	    ;;
	?)
	    usage
	    exit
	    ;;
	esac
done

if [[ -z $ON_OFF_FLAG ]]; then
    usage
    exit 1
fi

#
# inits
#------------------------------------------------------------------
DIR_BASE=/home/tmackall/bin
FILE_CAMERA_XML=${DIR_BASE}/cameras_ip/cameras.xml
FILE_CAMERA_XML_TMP=/tmp/cameras.$$.xml

#
# working XML file - create it if it is not there
#------------------------------------------------------------------
CAMERA_XML=$FILE_CAMERA_XML
ids=$(xmlstarlet sel  -t -m  "//camera" -v "@id" -o " "  ${CAMERA_XML})


#
# cameras.xml file - change it
#------------------------------------------------------------------
# case - ignore
shopt -s nocasematch;
for i in $ids; do
    echo $i
    if [[ $CAMERA_ALL_FLAG -eq 1 ]] || [[ $CAMLERA_LIST =~ $i ]]
    then
        echo made it
        item="/cameras/camera[@id=\"$i\"]/notifications_email"
        xmlstarlet ed -u ${item} -v ${ON_OFF_FLAG} ${CAMERA_XML} > $FILE_CAMERA_XML_TMP
        mv $FILE_CAMERA_XML_TMP ${CAMERA_XML}
    fi
done

rm $FILE_CAMERA_XML_TMP &> /dev/null
exit 0


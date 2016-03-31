#!/bin/bash
# ====================================================================================
#
# script that detects jpg files ftp'd to this machine.
#       - chooses a jpg to email with a zip file of all
#         the jpg files.
# ====================================================================================

DATE_FMT=$(date +%Y-%m-%d-%T)
DIR_BASE=/home/tmackall/bin
ZIP_FILE="/tmp/detected_files-${DATE_FMT}.zip"
PREV_FILES=/tmp/ftp_file_list.txt
FILE_CAMERA_XML=${DIR_BASE}/cameras_ip/cameras.xml
FILE_CAMERA_XML_TMP=/tmp/cameras.xml
LOGFILE_MOTION=/disk2/camera_log_motion/log.txt
MAX_SIZE=$((10 ** 7)) # 10M

EMAIL="mackall.tom@gmail.com,Malamack@gmail.com"
EMAIL="mackall.tom@gmail.com"
EMAIL_TEXT_FILE=/tmp/email_text_file.txt

FTP_DIR=/home/tmackall/ftp/

if [[ $# -eq 1 ]]; then
    LOGFILE_MOTION="$1"
    LOGFILE_MOTION+="/camera_log_motion/log.txt"
fi

echo $LOGFILE_MOTION

#
# xml - create it if it is not there
#---------------------------------------------------------------
difference=$(diff $FILE_CAMERA_XML $FILE_CAMERA_XML_TMP)
if [[ $? -eq 2 ]]; then
    echo "File does not exist"
    cp $FILE_CAMERA_XML $FILE_CAMERA_XML_TMP
elif [[ "$difference" != "" ]]; then
    echo "there is a difference creating a temp"
    echo "moving a new version of cameras.xml"
    cp $FILE_CAMERA_XML $FILE_CAMERA_XML_TMP
fi

#
# xml file - read it
#---------------------------------------------------------------
CAMERA_XML=$FILE_CAMERA_XML_TMP
notifs=$(xmlstarlet sel  -t -m  "//camera" -v "@id" -o ":" -v notifications_email -o " " ${CAMERA_XML})

# xml parse error - take it from git and pray that it works
status=$?
if [[ $status -ne 0 ]]; then
    echo "Error reading ${CAMERA_XML}, try to recover"
    git checkout -- $FILE_CAMERA_XML 
fi

# case insensitive regex
shopt -s nocasematch;

#
# main loop
#---------------------------------------------------------------
pics=""
camera_list=""
rm "$EMAIL_TEXT_FILE" >& /dev/null

# notifications - loop on cameras that have notifications turned on
for i in $notifs; do
    #
    # ftp dir - piece it together ftp/<camera id>
    camera=$(echo $i | sed 's/:.*//')
    dir="$FTP_DIR"
    dir+=$camera
    cd "${dir}"
 
    #
    # jpg's - put into an array
    files_temp=$(find $(pwd) -name "*.jpg")
    a_files=($files_temp)
    pics_num=${#a_files[@]}
    if [[ $pics_num -gt 0 ]]; then
        echo "${camera}, ${DATE_FMT}" >> "$LOGFILE_MOTION"
    fi
    echo $pics_num

    # notifications on? - yes, send some pics
    if [[ $i =~ :on ]]; then

	#
        # middle/center jpg - trying to get one with movement in it
        # zip and email jpgs 
        middle=$(($pics_num / 2))
        if [[ $pics_num -gt 0 ]]; then
            echo "Camera: ${camera}, num pics: ${pics_num}" >> \
                $EMAIL_TEXT_FILE
            camera_list+="$camera "
            pics+="-a ${a_files[$middle]} "
            zip -r ${ZIP_FILE} * > /dev/null
        fi
    fi
done

#
# movement check - no pics, no movement
#---------------------------------------------------------------
if [[ ! $pics == "" ]]; then
    motion_subject="\"Motion was detected on the following cameras: $camera_list\""
    filesize=$(stat -c%s "$ZIP_FILE")
    echo "Zip file:${ZIP_FILE} size: ${filesize}" >> "$EMAIL_TEXT_FILE"
    if [[ $filesize -ge $MAX_SIZE ]]; then
        echo "Zip file too large to attach" >> "$EMAIL_TEXT_FILE"
        cmd="mutt $EMAIL -s "${motion_subject}" $pics < $EMAIL_TEXT_FILE"
    else
        cmd="mutt $EMAIL -s "${motion_subject}" $pics -a ${ZIP_FILE} \
            < $EMAIL_TEXT_FILE"
    fi

    #
    # email - send it
    output=$(eval $cmd)
    echo "$output"
fi

#
# cleanup - remove all jpg's
#---------------------------------------------------------------
file_list=$(find $FTP_DIR -name "*.jpg")
for i in $file_list; do
    rm -rf "$i"
done
if [[ $filesize -lt $MAX_SIZE ]]; then
    rm "$ZIP_FILE" >& /dev/null
fi


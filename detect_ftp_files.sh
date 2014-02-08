#!/bin/bash

date_fmt=$(date +%Y-%m-%d-%T)
dir_base=/home/tmackall/bin
zip_file="/tmp/detected_files-${date_fmt}.zip"
prev_files=/tmp/ftp_file_list.txt
file_camera_xml=${dir_base}/cameras_ip/cameras.xml
file_camera_xml_tmp=/tmp/cameras.xml
logfile_motion=/disk2/camera_log_motion/log.txt
max_size=$((10 ** 7)) # 10M
email="mackall.tom@gmail.com,Malamack@gmail.com"
email_text_file=/tmp/email_text_file.txt
ftp_dir=/home/tmackall/ftp/


#
# xml - create it if it is not there
#---------------------------------------------------------------
difference=$(diff $file_camera_xml $file_camera_xml_tmp)
if [[ $? -eq 2 ]]; then
    echo File does not exist
    cp $file_camera_xml $file_camera_xml_tmp
elif [[ "$difference" != "" ]]; then
    echo there is a difference creating a temp
    echo moving a new version of cameras.xml
    cp $file_camera_xml $file_camera_xml_tmp
fi


# camera xml file - read it
CAMERA_XML=$file_camera_xml_tmp
notifs=$(xmlstarlet sel  -t -m  "//camera" -v "@id" -o ":" -v notifications_email -o " " ${CAMERA_XML})
#
# xml parse error - take it from git and pray that that works
status=$?
if [[ $status -ne 0 ]]; then
    echo "Error reading ${CAMERA_XML}, try to recover"
    git co -- $file_camera_xml 
fi

#
# case insensitive regex
shopt -s nocasematch;

#
# main loop
#---------------------------------------------------------------
pics=""
camera_list=""
rm "$email_text_file" >& /dev/null
for i in $notifs; do
    camera=$(echo $i | sed 's/:.*//')
    dir=$ftp_dir
    dir+=$camera
    cd "${dir}"
    files_temp=$(find $(pwd) -name "*.jpg")
    # array - put into
    a_files=($files_temp)
    pics_num=${#a_files[@]}
    if [[ $pics_num -gt 0 ]]; then
        echo "${camera}, ${date_fmt}" >> "$logfile_motion"
    fi
    echo $pics_num
    # check xml - do we send notifications?
    if [[ $i =~ :on ]]; then
        middle=$(($pics_num / 2))
        if [[ $pics_num -gt 0 ]]; then
            echo "Camera: ${camera}, num pics: ${pics_num}" >> \
                $email_text_file
            camera_list+="$camera "
            pics+="-a ${a_files[$middle]} "
            zip -r ${zip_file} * > /dev/null
        fi
    fi
done

#
# movement check - no pics, no movement
#---------------------------------------------------------------
if [[ ! $pics == "" ]]; then
    motion_subject="\"Motion was detected on the following cameras: $camera_list\""
    filesize=$(stat -c%s "$zip_file")
    echo "Zip file:${zip_file} size: ${filesize}" >> "$email_text_file"
    if [[ $filesize -ge $max_size ]]; then
        echo "Zip file too large to attach" >> "$email_text_file"
        cmd="mutt $email -s "${motion_subject}" $pics < $email_text_file"
    else
        cmd="mutt $email -s "${motion_subject}" $pics -a ${zip_file} \
            < $email_text_file"
    fi
    
    #
    # email - send it
    output=$(eval $cmd)
fi

#
# cleanup
#---------------------------------------------------------------
file_list=$(find $ftp_dir -name "*.jpg")
for i in $file_list; do
    rm -rf "$i"
done
if [[ $filesize -lt $max_size ]]; then
    rm "$zip_file" >& /dev/null
fi


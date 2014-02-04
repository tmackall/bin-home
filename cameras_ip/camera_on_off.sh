#!/bin/bash

dir_base=/home/tmackall/bin
prev_files=/tmp/ftp_file_list.txt
file_camera_xml=${dir_base}/cameras_ip/cameras.xml
file_camera_xml_tmp=/tmp/cameras.xml
flag_on_off="off"

#
# working XML file - create it if it is not there
shopt -s nocasematch;
echo $#
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <on/off>"
    exit
elif [[ "$1" =~ on ]]; then
    flag_on_off="on"
fi
echo $flag_on_off

email1="mackall.tom@gmail.com,Malamack@gmail.com"
email1="mackall.tom@gmail.com"
email_text_file=/tmp/email_text_file.txt
email_msg_body=/tmp/temp_email_body.txt
sample_pic=/tmp/sample.jpg
ftp_dir=/home/tmackall/ftp/
epoch_secs=$(date +%d-%b-%Y-%s)
tar_file="${ftp_dir}/tgz-d-files/detected_files.$epoch_secs.tgz"
max_size=10000000
period=60

CAMERA_XML=$file_camera_xml
ids=$(xmlstarlet sel  -t -m  "//camera" -v "@id" -o " "  ${CAMERA_XML})

#
# cameras.xml file - change it
for i in $ids; do
    item="/cameras/camera[@id=\"$i\"]/notifications_email"
    xmlstarlet ed -u ${item} -v ${flag_on_off} ${CAMERA_XML} > /tmp/t
    mv /tmp/t ${CAMERA_XML}
done
#
# delete the zip file
rm $zip_file >& /dev/null
shopt -s nocasematch;
for i in $notifs; do
    if [[ $i =~ :on ]]; then
        camera=$(echo $i | sed 's/:.*//')
        dir=$ftp_dir
        dir+=$camera
        cd "${dir}"
        zip -r ${zip_file} *
        echo $dir
    fi
done
file_list=$(find $ftp_dir -name "*.jpg")
for i in $file_list; do
    rm -rf "$i"
done
exit

#xmlstarlet sel -T -t -m "//camera" -i "@notifications_email=on" -v '@id' -o " " ${CAMERA_XML}
xmlstarlet sel  -t -m "//cameras"  -m "//camera" -v "@id" ${CAMERA_XML}
#xmlstarlet sel -t -m "//camera" -v "@id" -o " " ${CAMERA_XML}
exit
#
# grab the unique camera IDs from the XML
ids=$(xmlstarlet sel -t -m "//camera" -v "@id" -o " " ${CAMERA_XML})
rm $zip_file >& /dev/null

# see how many tgz files have been created in the last hour. Quit
# sending if more than 3
tgz_cnt=$(find $ftp_dir -mmin -${period}  -name "*.tgz" | wc | \
    sed 's/[0-9]\+ \+\([0-9]\+\) .*/\1/' )

tot_size=0
#
# get the size of the tgz files in the past hour
if [[ $tgz_cnt -gt 0 ]]; then
    tgz_files=$(find $ftp_dir -mmin -${period}  -name "*.tgz" )
    tot_size=$(du -cb $tgz_files | grep total$ |\
        sed -e 's/\([0-9]\+\)\s\+total/\1/')
fi

# any jpg files here mean they are new since we tar them up
file_list=$(find $ftp_dir -name "*.jpg")
echo "$file_list"
status=$?
if [[ $status -ne 0 ]]; then
    fail_text="find command failed: $status"
    echo $fail_text
    mutt $email1 -s "$fail_text" < /dev/null
fi

# bail if there are no new .jpg's
if [[ $file_list == "" ]]; then
    echo "no files"
    exit 0
fi
#
# grab a single jpeg in the middle to send as a sample
cameras=$(echo "$file_list" | sed 's/\(.*\)\/.*/\1/' | sort | uniq | sed 's/.*\///') 
pics=""
for i in $cameras; do
    cam_file_list=$(echo "$file_list" | grep $i)
    file_cnt=$(echo "$cam_file_list" | wc | sed 's/[0-9]\+ \+\([0-9]\+\) .*/\1/')
    a_files=($cam_file_list)
    middle=$(($file_cnt / 2))
    pics="$pics -a ${a_files[$middle]}"
    #cp $temp_jpg $sample_pic
done
echo "$pics"

motion_string=""
temp_file="/tmp/detect_ftp_files.tmp"
rm $temp_file
touch $temp_file
#
# zip files to put in an email
cd "${ftp_dir}"
for file_and_path in ${file_list}; do

    # remove the path so that the extraction is cleaner
    file=$(echo $file_and_path | sed 's/.*\///')

    # zip the files
    zip -g $zip_file ${file_and_path}

    # check to see what camera detected motion
    for i in $ids; do
        if [[ $file_and_path =~ $i ]]; then
            echo -e $i >> $temp_file
        fi
    done
done

motion_string=$(cat $temp_file | sort | uniq)
echo $motion_string
#
# message subject line
motion_subject="\"Motion was detected on the following cameras: $motion_string\""
echo $motion_subject

# tar up the files in the ftp dir to reduce space and clutter.
#cd ${ftp_dir}
echo $file_list
tar -czf ${tar_file} $file_list >& /dev/null
status=$?
echo "tar: $status"


#
# only send email if there are new jpgs - tar will return 2 if there
# are no jpegs
if [[ $status -eq 0 ]]; then

    # get some ftp dir info
    echo -e "Number of image files: $file_cnt\n" > $email_text_file
    #echo -e "$(pwd)\n" >> $email_text_file
    #echo -e "$(ls -lrt | \
    #    sed 's/.* \+\(... \+[0-9]\+ \+[0-9]\{2\}:.*\)/\1/')\n" >> \
    #    $email_text_file
    disk_use=$(df -a . | grep -Po "\d+%" )
    echo -e "Use: $disk_use\n" >> $email_text_file
    
    # for txt email only
    echo -e $motion_subject > $email_msg_body
    echo -e "disk use: $disk_use, Num imgs: $file_cnt" >> $email_msg_body
#    mutt $email_msg_only -s "Motion detection alert!"  < $email_msg_body
    # send the zipped jpg files
    if [[ $tot_size -ge $max_size ]]; then
        echo -e "\nHalted sending pics due to size: $tot_size"\
            >> $email_text_file
        #cmd="mutt $email1 -s "${motion_subject}"  < $email_text_file"
        cmd="mutt $email1 -s "${motion_subject}" $pics -a $zip_file \
            < $email_text_file"
    else
        cmd="mutt $email1 -s "${motion_subject}" $pics -a $zip_file \
            < $email_text_file"
    fi
    output=$(eval $cmd)
    rm $file_list
    status=$?
else
    # will create an empty tar file that I don't want
    echo "rm: $status"
    rm ${tar_file}
fi

exit 0


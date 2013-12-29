#!/bin/bash
source ~/.bashrc

email_list="mackall.tom@gmail.com"
email_text_file=/tmp/email_text_file.txt
email_msg_body=/tmp/temp_email_body.txt
ftp_dir=/home/tmackall/ftp
epoch_secs=$(date +%d-%b-%Y-%s)
zip_file="/tmp/detected_files_${epoch_secs}.zip"
disk_home_server="/disk1/mackall-rp03/ftp"

# any jpg files here mean they are new since we tar them up
file_list=$(find $ftp_dir -name "*.jpg")
echo "$file_list"
status=$?
if [[ $status -ne 0 ]]; then
    fail_text="find command failed: $status"
    echo $fail_text
    mutt $email_list -s "$fail_text" < /dev/null
fi

# bail if there are no new .jpg's
if [[ $file_list == "" ]]; then
    echo "no files"
    exit 0
fi


# grab a single jpeg in the middle to send as a sample
file_cnt=$(echo "$file_list" | wc | sed 's/[0-9]\+ \+\([0-9]\+\) .*/\1/')
a_files=($file_list)
middle=$(($file_cnt / 2))
pics="${a_files[$middle]}"
echo "$pics"
motion_string=""

# zip files to put in an email
cd "${ftp_dir}"
for file_and_path in ${file_list}; do

    # remove the path so that the extraction is cleaner
    file=$(echo $file_and_path | sed 's/.*\///')

    # zip the files
    #zip -g $zip_file ${file_and_path}
    zip -g $zip_file ${file} > /dev/null

done

# email subject
motion_string="Condo-Cam"

# message subject line
motion_subject="\"Motion was detected on the following cameras: $motion_string\""


# get some ftp dir info
echo -e "Number of image files: $file_cnt\n" > $email_text_file
disk_use=$(df -a . | grep -Po "\d+%" )

# for txt email only
echo -e $motion_subject > $email_msg_body
echo -e "disk use: $disk_use, Num imgs: $file_cnt" >> $email_msg_body
echo -e "location: $disk_home_server, file:$zip_file" >> $email_msg_body

# email notification
cmd="mutt $email_list -s "${motion_subject}" -a $pics < $email_msg_body"
output=$(eval $cmd)
status=$?


# ZIP file - move to home server
cmd="scp $zip_file mackall-home:/${disk_home_server}/"
output=$(eval $cmd)

# cleanup
rm $file_list
rm $zip_file

exit $status

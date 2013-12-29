#!/bin/bash
source ~/.bashrc

zip_file=/tmp/detected_files.zip
prev_files=/tmp/ftp_file_list.txt
email1="mackall.tom@gmail.com"
email_text_file=/tmp/email_text_file.txt
email_msg_only=3032411300@txt.att.net
email_msg_body=/tmp/temp_email_body.txt
ftp_dir=/home/tmackall/ftp
epoch_secs=$(date +%d-%b-%Y-%s)

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
file_cnt=$(echo "$file_list" | wc |\
    sed 's/[0-9]\+ \+\([0-9]\+\) .*/\1/')
a_files=($file_list)
middle=$(($file_cnt / 2))
pics="${a_files[$middle]}"
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
    #zip -g $zip_file ${file_and_path}
    zip -g $zip_file ${file}

done

#motion_string=$(cat $temp_file | sort | uniq)
motion_string="Condo-Cam"
#
# message subject line
motion_subject="\"Motion was detected on the following cameras: $motion_string\""
echo $motion_subject


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
# send the zipped jpg files
cmd="mutt $email1 -s "${motion_subject}" -a $pics -a $zip_file \
    < $email_text_file"
output=$(eval $cmd)
status=$?
rm $file_list
rm $zip_file

exit $status



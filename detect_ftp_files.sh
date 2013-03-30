#!/bin/bash
source ~/.bashrc

zip_file=/tmp/detected_files.zip
prev_files=/tmp/ftp_file_list.txt
email1=mackall.tom@gmail.com
email_text_file=/tmp/email_text_file.txt
email_msg_only=3032411300@txt.att.net
email_msg_body=/tmp/temp_email_body.txt
ftp_dir=~/ftp
tar_file="$ftp_dir/detected_files.$$.tgz"
max_per_period=3
period=60

rm $zip_file

# see how many tgz files have been created in the last hour. Quit
# sending if more than 3
#echo $(find "$ftp_dir" -mmin -${period}  -name "*.tgz")
tgz_cnt=$(find "$ftp_dir" -mmin -${period}  -name "*.tgz" | wc | \
    sed 's/\([0-9]\+\) .*/\1/' )
#echo $tgz_cnt

# any jpg files here mean they are new since we tar them up
file_list=$(find "${ftp_dir}" -name "*.jpg" )
status=$?
if [[ $status -ne 0 ]]; then
    fail_text="find command failed: $status"
    echo $fail_text
    mutt $email1 -s "$fail_text" < /dev/null
fi


f_kitchen=0
f_basement=0
#
# zip files to put in an email
for file in ${file_list}; do
    zip -g $zip_file ${file}
    # check to see what camera detected motion
    if [[ $file =~ kitchen ]]; then
        f_kitchen=1
    elif [[ $file =~ basement ]]; then
        f_basement=1
    fi
done


#
# message subject line
echo "Camera count: $(($f_kitchen + $f_basement))"
motion_subject=""
if [[ $f_kitchen -eq 1 ]] && [[ $f_basement -eq 1 ]]; then
    motion_subject="Motion was detected in the kitchen and basement"
elif [[ $f_kitchen -eq 1 ]]; then
    motion_subject="Motion was detected in the kitchen"
else
    motion_subject="Motion was detected in the basement"
fi


# tar up the files in the ftp dir to reduce space and clutter.
cd ${ftp_dir}
tar -czf ${tar_file} *.jpg >& /dev/null
status=$?
echo "tar: $status"

#
# only send email if there are new jpgs - tar will return 2 if there
# are no jpegs
if [[ $status -eq 0 ]]; then
    rm ${ftp_dir}/*.jpg

    # get some ftp dir info
    echo -e "$(pwd)\n" > $email_text_file
    echo -e "$(ls -lrt | \
        sed 's/.* \+\(... \+[0-9]\+ \+[0-9]\{2\}:.*\)/\1/')\n" >> \
        $email_text_file
    echo -e "Use: $(df -a . | grep -Po "\d+%" )\n" >> $email_text_file
    
    # for txt email only
    echo -e $motion_subject > $email_msg_body
    mutt $email_msg_only -s "Motion detection alert!"  < $email_msg_body
    # send the zipped jpg files
    if [[ $tgz_cnt -gt 2 ]]; then
        echo -e "\nHalted sending pics due to freqency: $tgz_cnt per $period mins" >> $email_text_file
        mutt $email1 -s "$motion_subject"  < $email_text_file
    else
        mutt $email1 -s "$motion_subject" -a $zip_file < $email_text_file
    fi
    echo $?
else
    # will create an empty tar file that I don't want
    rm ${tar_file}
fi

exit 0



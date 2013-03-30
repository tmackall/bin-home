#!/bin/bash
source ~/.bashrc

zip_file=/tmp/detected_files.zip
prev_files=/tmp/ftp_file_list.txt
email1=mackall.tom@gmail.com
email_text_file=/tmp/email_text_file.txt
ftp_dir=~/ftp
tar_file="$ftp_dir/detected_files.$$.tgz"

# any jpg files here mean they are new since we tar them up
#file_list=$(find "${ftp_dir}" -cnewer $zip_file -name "*.jpg" )
file_list=$(find "${ftp_dir}" -name "*.jpg" )
status=$?
if [[ $status -ne 0 ]]; then
    fail_text="find command failed: $status"
    echo $fail_text
    mutt $email1 -s "$fail_text" < /dev/null
fi


#
# zip files to put in an email
echo $file_list
for file in ${file_list}; do
    zip -g $zip_file ${file}
done

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
    pwd > $email_text_file
    ls -l >> $email_text_file
    df -a . >> $email_text_file
    mutt mackall.tom@gmail.com -s "Motion detection alert" \
        -a $zip_file < $email_text_file
    rm $zip_file
    echo $?
else
    rm ${tar_file}
fi

exit 0



#!/bin/bash
script=$0
email_addrs=mackall.tom@gmail.com

# these are the filesystem we are concerned with

# key-value pairs for filesystems
declare -A fsArr
fsArr["/"]=13
fsArr["/disk1"]=76
fsArr["/disk2"]=10
fsArr["/disk3"]=98

# spin the file system array
for fs in ${!fsArr[@]}; do
    th=${fsArr[${fs}]}
    gd=$(which get_disk_space_pcent.sh)
    if [[ $gd == "" ]]; then
        subject="get_disk_space_pcent.sh not found"
        mutt -s "$subject" $email_addrs < /dev/null
        continue
    fi
    output=$(eval "$gd $fs")
    status=$?
    if [[ $status -ne 0 ]]; then
        subject="$script failed with error code: $status"
        echo -e $output | mutt -s "$subject" $email_addrs
        continue 
    fi
    if [[ $output -gt $th ]]; then
        host=$(hostname)
        subject="Filesystem \"$fs\" threshold exceeded ($th%) for host:$host"
        echo -e "Current use: ${output}%" | mutt -s "$subject" $email_addrs
    fi
done

exit 0

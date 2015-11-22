#!/bin/bash
script=$0
email_addrs=mackall.tom@gmail.com

# these are the filesystem we are concerned with

# key-value pairs for filesystems
declare -A fsArr
fsArr["/"]=45
#fsArr["/disk1"]=85
fsArr["/disk2"]=95

# spin the file system array
for fs in ${!fsArr[@]}; do
    th=${fsArr[${fs}]}
    gd="/home/tmackall/bin/get_disk_space_pcent.sh"
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

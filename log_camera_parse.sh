#!/bin/bash

dir_log=/disk2/camera_log_motion
data=$(cat ${dir_log}/log.txt | sed 's/ *//g')
dir_video=/disk2/camera_video_backups
dir_copy=/disk3/video_cam_mvmt

#
# put the time into the name
file_name_adj_list=""
pushd "$dir_video"
for i in $(ls  *.mp4); do
    time=$(ls -l $i | awk '{print $8;}')
    file_new=$(echo $i |\
        sed  "s/-[0-9]\+:[0-9]\+:/-$time:/")
    file_name_adj_list+="$file_new  "
done
popd
for i in $file_name_adj_list; do
    echo $i
done
exit
for i in $data; do
    file_search=$(echo $i | sed 's/\(.*\),\(.*\):..$/\2*_\1.mp4/')
    file_name=$(find $dir_video -name $file_search)
    echo "file name:$file_name"
    if [[ ! file_name == "" ]]; then
        cmd="mv $file_name $dir_copy"
        echo $cmd
        #eval "$cmd"
    fi
done
tail -n 6 "${dir_log}/log.txt" > /tmp/log.txt
mv /tmp/log.txt "${dir_log}/log.txt"
exit 0


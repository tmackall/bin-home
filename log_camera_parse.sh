#!/bin/bash

#
# init
#------------------------------------------------------------
dir_log=/disk2/camera_log_motion
data=$(cat ${dir_log}/log.txt | sed 's/ *//g')
dir_video=/disk2/camera_video_backups
dir_video_storage=/disk1/video_storage

#
# video files 
#------------------------------------------------------------
pushd "$dir_video"
for i in $(ls); do
    # time - last modified. The filename is a creation time.
    stuff=$(ls -l --time-style=full-iso $i | awk '{print $6,$7,$9}')
    time_fmt=$(echo $stuff | awk '{print $1,$2}')
    file_time=$(echo $stuff | awk '{print $3}')
    camera=$(echo $i | sed s/.*_// | sed 's/\..*//')
    time=$(echo $i | sed s/_.*//)
    time_epoch=$(date -d "$time_fmt" +%s)
    videos_tmp+="$camera:$time_epoch;$i "
done
popd "$dir_video"

#
# hash on video - bash4 dependency
# this allows faster correlation with log triggers
#------------------------------------------------------------
declare -A video_array
for i in $videos_tmp; do
    key=$(echo $i | sed 's/;.*//')
    value=$(echo $i | sed 's/.*;//')
    video_array[$key]=$value
done

#
# data triggers from log
#------------------------------------------------------------
for i in $data; do
    camera=$(echo $i | sed s/,.*//)
    time=$(echo $i | sed s/.*,//)
    time_fmt=$(echo $time | sed 's/-\(..:.*\)$/ \1/') 
    time_epoch=$(date -d "$time_fmt" +%s)
    log_trig_temp+="$camera:$time_epoch "
done

video_move_list=""
for i in $log_trig_temp; do
    cam=$(echo $i | sed s/:.*//)
    time=$(echo $i | sed s/.*://)
    for ((j=0;j<=5;j++)); do
        time_adj=$(($time+$j))

        if [[ ! ${video_array[$cam:$time_adj]} == "" ]]; then
            if [[ $j -gt 0 ]]; then
                echo Time $time_adj was different than expected: $time
            fi
            #echo found one $(date -d @$time) - \
            #     ${video_array[$cam:$time_adj]}
            video_move_list+="${video_array[$cam:$time_adj]} "
            break
        fi
    done
done

#
# update the log file
#------------------------------------------------------------
tail  "${dir_log}/log.txt" > /tmp/log.txt
mv /tmp/log.txt "${dir_log}/log.txt"

#
# move the files to perm storage
#------------------------------------------------------------
for i in $video_move_list; do
    echo moving $i
    mv "$dir_video/$i" "$dir_video_storage"
done

exit 0


#!/bin/bash

# video length needs to be passed in in minutes
# ------------------------------------------------------------
MINS_VIDEO=$1

#
# init
# -----------------------------------------------------------
dir_log=/disk2/camera_log_motion
DATA=$(cat ${dir_log}/log.txt | sed 's/ *//g')
dir_video=/disk2/camera_video_backups
dir_video_storage=/disk2/video_storage
#SECS_VIDEO_LEN=$(($MINS_VIDEO*60*60))


# video files
# ls the video files dir. File time is from the start and
# use the modify time to map to the trigger detection time.
# -----------------------------------------------------------
pushd "$dir_video"
for i in $(find . -type f -mmin -90 -print); do
    # time - last modified. The filename is a creation time.
    stuff=$(ls -l --time-style=full-iso $i | awk '{print $6,$7,$9}')
    time_fmt=$(echo $stuff | awk '{print $1,$2}')
    file_time=$(echo $stuff | awk '{print $3}')
    camera=$(echo $i | sed s/.*_// | sed 's/\..*//')
    time=$(echo $i | sed s/_.*//)
    time_epoch=$(date -d "$time_fmt" +%s)
    videos_tmp+="$camera:$time_epoch;$i "
done
popd

#
# video - create a hash of video data
# this allows faster correlation with log triggers
# -----------------------------------------------------------
declare -A video_array
for i in $videos_tmp; do
    key=$(echo $i | sed 's/;.*//')
    value=$(echo $i | sed 's/.*;//')
    video_array[$key]=$value
done

#
# data triggers from log
# the time on these are the end of the trigger period.
# -----------------------------------------------------------
for i in $DATA; do
    camera=$(echo $i | sed s/,.*//)
    time=$(echo $i | sed s/.*,//)
    time_fmt=$(echo $time | sed 's/-\(..:.*\)$/ \1/') 
    time_epoch=$(date -d "$time_fmt" +%s)
    log_trig_temp+="$camera:$time_epoch "
done

#
# correlation - map the triggers to the video files.
# find the videos that have movement. Loop on log triggers
# ------------------------------------------------------------
video_move_list=""
for i in $log_trig_temp; do
    cam=$(echo $i | sed s/:.*//)
    time=$(echo $i | sed s/.*://)
    #
    # times should be on 10 min intervals. This allows them
    # to be 5 secs off
    for ((j=0;j<=5;j++)); do
        time_adj=$(($time+$j))

        if [[ ! ${video_array[$cam:$time_adj]} == "" ]]; then
            if [[ $j -gt 0 ]]; then
                echo Time $time_adj was different than expected: $time
            fi
            video_move_list+="${video_array[$cam:$time_adj]} "
            break
        fi
    done
done

#
# update the log file
# leave 10 entries in the log file incase there are
# video files that are not ready (although there should not be)
# -----------------------------------------------------------
tail  "${dir_log}/log.txt" > /tmp/log.txt
mv /tmp/log.txt "${dir_log}/log.txt"

#
# move the files to perm storage
# -----------------------------------------------------------
for i in $video_move_list; do
    echo moving $i
    mv "$dir_video/$i" "$dir_video_storage"
done

exit 0

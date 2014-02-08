#!/bin/bash

#
# init
#------------------------------------------------------------
dir_log=/disk2/camera_log_motion
data=$(cat ${dir_log}/log.txt | sed 's/ *//g')
dir_video=/disk2/camera_video_backups
dir_copy=/disk3/video_cam_mvmt

#
# video files 
#------------------------------------------------------------
file_videos_tmp="/tmp/file_videos_tmp.$$.txt"
echo "" > $file_videos_tmp
pushd "$dir_video"
for i in $(ls); do
    stuff=$(ls -l --time-style=full-iso $i | awk '{print $6,$7,$9}')
    time_fmt=$(echo $stuff | awk '{print $1,$2}')
    file_time=$(echo $stuff | awk '{print $3}')
    camera=$(echo $i | sed s/.*_// | sed 's/\..*//')
    time=$(echo $i | sed s/_.*//)
    time_epoch=$(date -d "$time_fmt" +%s)
    echo "$camera:$time_epoch:$time:v" >> $file_videos_tmp
done
popd "$dir_video"

#
# data triggers from log
#------------------------------------------------------------
file_data_tmp="/tmp/file_data_tmp.$$.txt"
echo "" > $file_data_tmp
for i in $data; do
    camera=$(echo $i | sed s/,.*//)
    time=$(echo $i | sed s/.*,//)
    time_fmt=$(echo $time | sed 's/-\(..:.*\)$/ \1/') 
    time_epoch=$(date -d "$time_fmt" +%s)
    echo "$camera:$time_epoch:$time:l" >> $file_data_tmp
done


#
# data - move around and sort it.
#------------------------------------------------------------
file_combined="/tmp/file_combined.$$.txt"
file_combined_sorted="/tmp/file_combined_sorted.$$.txt"
cat $file_videos_tmp > $file_combined
cat $file_data_tmp >> $file_combined
cat $file_combined | sort > $file_combined_sorted
echo $file_combined_sorted

#
# cleanup
#------------------------------------------------------------
rm $file_videos_tmp
rm $file_data_tmp
rm $file_combined
#tail -n 6 "${dir_log}/log.txt" > /tmp/log.txt
#mv /tmp/log.txt "${dir_log}/log.txt"
exit 0
#

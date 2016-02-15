#!/bin/bash

#
# grab the unique camera IDs from the XML
vals=$(xmlstarlet sel -t -m "//camera" -v "@id" -o ":" -v "status" \
    -o " " ${CAMERA_XML})
match=0
cams_online=""
#
# loop - all unique IDs
for i in $vals
do
    cam_id=$(echo $i | sed 's/\(.*\):.*/\1/')
    status=$(echo $i | sed 's/.*:\(.*\)/\1/')
    if [[ $status =~ online ]]; then
        cams_online="$cams_online $cam_id"
    fi
done
#
# create a tmp file, delay a sec, and see if the cam files are newer
test_file="/tmp/t"
touch $test_file
sleep 1

cams_dead=""
for i in $cams_online; do
    disk_loc=$(xmlstarlet sel -t -m "//camera[@id='$i']" \
        -v "disk_location" ${CAMERA_XML})
    file_re="${disk_loc}/.*_${i}\.mp4"
    active_file=$(find $disk_loc -newer $test_file | grep "$file_re")
    if [[ $active_file =~ ^\ *$ ]]; then
        cams_dead="$cams_dead $i"
    else
        echo "File: $active_file is active"
    fi

done
echo $cams_dead

for cam_id in $cams_dead; do
    #
    # KILL could be multiple processes
    cam_id_re="_${cam_id}\."
    pid_to_kill=$(ps -eaf | grep -i vlc | grep "${cam_id_re}" | \
        sed  's/^[^  ]\+ \+\([0-9]\+\).*/\1/')
    for i in $pid_to_kill; do
        if [[ $i =~ ^[0-9]+$ ]]; then
            kill -9 $i
        else
            echo "Error: could not find vlc process: $pid_to_kill"
        fi
    done

    # TIME - compute the time until the next hour
    hour_curr=$(date +%k)
    num_secs_until_hour=$(($(date -d ${hour_curr}:59:59 +%s) - \
        $(date +%s) + 1))
    echo "Num seconds until the top of the hour: $num_secs_until_hour"

    mutt mackall.tom@gmail.com -s "restarting camera: $cam_id" < /dev/null
    status=$(nohup ${CAMERA_HOME}/camera_capture.sh $cam_id $num_secs_until_hour > /dev/null&)
    echo "status: $status"
done
exit 0


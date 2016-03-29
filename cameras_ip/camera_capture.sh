#!/bin/bash
# =======================================================
#
# script to capture video via real
# time streaming protocol (rtsp)
#
# =======================================================
date_name=$(date +"%Y-%m-%d-%H:%M:%S")
time_secs=$((60 * 60))

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <camera id> <time (in secs)> [root dir]\n"
    exit 2
fi

cam_id=$1
time_secs=$2
#
# root dir - optional
if [[ $3 == "" ]]; then
    ROOT="/disk2"
else
    ROOT=$3
fi

CAMERA_XML="/home/tmackall/bin/cameras_ip/cameras.xml"

#
# grab the unique camera IDs from the XML
vals=$(xmlstarlet sel -t -m "//camera" -v "@id" -o " " ${CAMERA_XML})
match=0

#
# loop - all unique IDs
for i in $vals
do
    if [[ $i =~ ^$cam_id$ ]]; then
        echo "match"
        match=1
    fi
done
if [[ $match -eq 0 ]]; then
    echo "$cam_id not found."
    exit 3
fi
#
# xml - get rtsp info for the camera
# ------------------------------------------------------------
cam_ip=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "ip_address" ${CAMERA_XML})
cam_url=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "rtsp_loc" ${CAMERA_XML})
cam_user=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "user" ${CAMERA_XML})
cam_pass=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "passwd" ${CAMERA_XML})
rstp_cmd="rtsp://${cam_ip}/${cam_url} --rtsp-user=${cam_user} --rtsp-pwd=${cam_pass}"
name="${date_name}_${cam_id}.mp4"
cmd="cvlc --run-time ${time_secs} --rtsp-tcp  $rstp_cmd --sout=\"#duplicate{dst=standard{access=file,dst='${ROOT}/camera_video_backups/${name}',mux=mp4}\" vlc://quit"
echo "$cmd"
eval $cmd
status=$?
echo "Status:$status from command: \"$cmd\"" > /tmp/t
if [[ $status -ne 0 ]]; then
    mutt mackall.tom@gmail.com -s "Video capture failed for: ${name}"\
        < /tmp/t
fi
exit 0

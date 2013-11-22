#!/bin/bash
date_name=$(date +"%Y-%m-%d-%H:%M:%S")
time_secs=$((60 * 60))

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <camera id> <time>\n"
    exit 2
fi

cam_id=$1
time_secs=$2
#
# grab the unique camera IDs from the XML
vals=$(xmlstarlet sel -t -m "//camera" -v "@id" -o " " cameras.xml)
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
cam_ip=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "ip_address" cameras.xml)
cam_url=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "rtsp_loc" cameras.xml)
cam_user=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "user" cameras.xml)
cam_pass=$(xmlstarlet sel -t -m "//camera[@id='$cam_id']" \
    -v "passwd" cameras.xml)
rstp_cmd="rtsp://${cam_ip}/${cam_url} --rtsp-user=${cam_user} --rtsp-pwd=${cam_pass}"
name="${date_name}_${cam_id}.mp4"
cmd="cvlc --run-time ${time_secs}  $rstp_cmd --sout=\"#duplicate{dst=standard{access=file,dst='/disk2/camera_video_backups/${name}',mux=mp4}\" vlc://quit"
eval $cmd
status=$?
echo "Status:$status from command: \"$cmd\"" > /tmp/t
if [[ $status -ne 0 ]]; then
    mutt mackall.tom@gmail.com -s "Video capture failed for: ${name}"\
        < /tmp/t
fi
exit 0

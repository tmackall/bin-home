#!/bin/bash

date_name=$(date +"%Y-%m-%d-%H:%M:%S")
ip_ps01="192.168.1.44"
time_secs=3800

#
# cmd line input - we need cam-specific information (name and address)
if [[ $# -eq 3 ]]; then
    time_secs=$3
elif [[ $# -ne 2 ]]; then
    printf "\nUsage: $0 <ip-address> <camera name>\n"
    exit 2
fi
cam_ip=$1
cam_name=$2

#
# rstp cmd - create the unique portion of this
if { [[ "$cam_name" =~ ^ps ]] || [[ "$cam_name" =~ ^PS ]]; } then
    rstp_cmd="rtsp://${cam_ip}/nphMpeg4/g726-640x480 --rtsp-user=tmackall --rtsp-pwd=templeAve1"
else
    rstp_cmd="rtsp://${cam_ip}/H.264/media.smp --rtsp-user=admin --rtsp-pwd=dampob12" 
fi

printf "${time_secs} $rstp_cmd\n"

name="${date_name}_${cam_name}.mp4"
cmd="cvlc --run-time ${time_secs}  $rstp_cmd --sout=\"#duplicate{dst=standard{access=file,dst='/disk2/camera_video_backups/${name}',mux=mp4}\" vlc://quit"
echo "$cmd"
eval $cmd

status=$?
echo "Status:$status from command: \"$cmd\"" > /tmp/t
if [[ $status -ne 0 ]]; then
    mutt mackall.tom@gmail.com -s "Video capture failed for: ${name}" < /tmp/t
fi

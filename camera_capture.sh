#!/bin/bash

date_name=$(date +"%Y-%m-%d-%H:%M:%S")
ip_sno01="192.168.1.15"

name="${date_name}_sno01.mp4"
output=$(cvlc --run-time 30 rtsp://${ip_sno01}/H.264/media.smp --rtsp-user=admin --rtsp-pwd=dampob12 --sout="#duplicate{dst=standard{access=file,dst='/home/tmackall/video/${name}',mux=mp4}" vlc://quit)


status=$?
echo $status
if [[ $status -ne 0 ]]; then
    mutt mackall.tom@gmail.com -s "Video capture failed for: ${name}" < /dev/null
fi

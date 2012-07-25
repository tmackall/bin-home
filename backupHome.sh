#!/bin/bash
tar -zcvf /tmp/mackall-media-`date +"%m-%d-%y"`.tgz -X /home/tmackall/bin/exclude.txt /home/tmackall
echo "backup is located at /tmp/mackall-media-`date +"%m-%d-%y"`.tgz"
#scp /tmp/mackall-media-`date +"%m-%d-%y"`.tgz "tmackall-mac1.local:/Volumes/JULY-BCK/"
#rm /tmp/mackall-media-`date +"%m-%d-%y"`.tgz

#!/bin/bash
tar -zcvf /tmp/mackall-lnx2-`date +"%m-%d-%y"`.tgz -X /home/tmackall/bin/exclude.txt /home/tmackall
echo "backup is locatedf at /tmp/mackall-lnx2-`date +"%m-%d-%y"`.tgz"
scp /tmp/mackall-lnx2-`date +"%m-%d-%y"`.tgz "tmackall-mac.local:/Volumes/BACKUP\ #3/"
#rm /tmp/mackall-lnx2-`date +"%m-%d-%y"`.tgz

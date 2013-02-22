#!/bin/bash
source /home/tmackall/.bashrc
#for i in / /disk1 /disk2 /disk3; do 
~/bin/get_disk_space.py --fs / --th 12
~/bin/get_disk_space.py --fs /disk1 --th 65
~/bin/get_disk_space.py --fs /disk2 --th 10
~/bin/get_disk_space.py --fs /disk3 --th 98

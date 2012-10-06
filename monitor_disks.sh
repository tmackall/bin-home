#!/bin/bash
source /home/tmackall/.bashrc
#for i in / /disk1 /disk2 /disk3; do 
~/develop/get_disk_space.py --fs / --th 10
~/develop/get_disk_space.py --fs /disk1 --th 50
~/develop/get_disk_space.py --fs /disk2 --th 10
~/develop/get_disk_space.py --fs /disk3 --th 98

#!/bin/bash
cd /mnt/AU_LINUX_ANDROID
#AU_REV=01.08.00.010
AU_REV=$1
export P4CLIENT=TMACKALL_ANDROID 
p4 sync @AU_LINUX_ANDROID_CUPCAKE.$AU_REV
cd TMACKALL_ANDROID/release/android/$AU_REV
echo $ getvus android.plf


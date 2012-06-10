#!/bin/bash
export TERM=vt100
export TESTHM=/local/mnt/workspace/tmackall
~/bin/aBuild.exp nightly 
echo "Nightly finished\!" >> /tmp/build.log

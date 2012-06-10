#!/bin/bash
args=("$@")
start=`date`
echo $start
#
#echo arguments to the shell
job=${args[0]}
ectool  login "admin" "changeme"
ectool  getJobDetails $job | tee /tmp/${job}.xml


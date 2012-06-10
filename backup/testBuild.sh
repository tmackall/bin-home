#!/bin/bash
args=("$@")
start=`date`
echo $start
umask 022
target=${args[0]}
echo $target
case "$target" in
	'7200') runProc=run7200.sh;;
	'7225') runProc=run7225.sh;;
	'8650') runProc=run8650.sh;;
	*) echo "no match";return 1;;

esac
echo "${runProc}"
$runProc
echo "start: ${start}"
echo "end:   `date`"


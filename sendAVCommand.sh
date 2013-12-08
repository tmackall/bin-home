#!/bin/bash
#echo -ne $2\\r | nc -w1 -o $3 $1 23
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <ip address> <command>"
    exit 2
fi
cmd="echo -ne $2\\\\r | nc -w1 $1 23"
echo "$cmd"
status=$(eval $cmd)

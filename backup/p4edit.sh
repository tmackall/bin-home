#!/bin/bash
args=("$@")
#echo arguments to the shell
export P4CLIENT=${args[0]}
p4 client

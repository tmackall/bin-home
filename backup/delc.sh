#!/bin/bash
args=("$@")
#echo arguments to the shell
p4 client -d  ${args[0]}

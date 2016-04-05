#!/bin/bash


if [[ $# < 1 ]]; then
    DELAY_MAX=60
else
    DELAY_MAX=$1
fi


T=$[ ( $RANDOM % ${DELAY_MAX} ) + 1] && sleep ${T}s


#!/bin/bash

CHANGE=$1
if [ "$2" == "" ]; then
   CHANGE_MINUS_ONE=$(($CHANGE - 1))
else
   echo "reverting back to $2"
   CHANGE_MINUS_ONE=$2
fi

echo "CHANGE is $CHANGE, CHANGE -1 is $CHANGE_MINUS_ONE"

p4 sync @$CHANGE_MINUS_ONE
p4 files @=$CHANGE | sed -n -e "s/#.* - delete .*//p" | p4 -x- add
p4 files @=$CHANGE | sed -n -e "s/#.* - edit .*//p" | p4 -x- edit
p4 files @=$CHANGE | sed -n -e "s/#.* - integrate .*//p" | p4 -x- edit
p4 sync
p4 files @=$CHANGE | sed -n -e "s/#.* - add .*//p" | p4 -x- delete
p4 files @=$CHANGE | sed -n -e "s/#.* - branch .*//p" | p4 -x- delete
p4 resolve -ay

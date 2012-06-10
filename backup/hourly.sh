#!/bin/bash
export TERM=vt100
export USER=tmackall
branch=gb
export WSHOME=/local/mnt/workspace/tmackall/$branch
cd $WSHOME/automation/tools/ci_tools/poll_gerrit
./getChangeBacklog.exp gingerbread ics -e abait.stats.hourly@qualcomm.com
./getChangeBacklog.exp honeycomb_mr2_mainline  -e abait.stats.hourly@qualcomm.com
cd $WSHOME
~/bin/repo sync
branch=ics
export WSHOME=/local/mnt/workspace/tmackall/$branch
cd $WSHOME
~/bin/repo sync


#!/bin/bash
export TERM=vt100
# get the preflight status for the day
~/bin/getStabilityStatus.exp 1 1
# get the mainline health for the day
~/bin/getStabilityStatus.exp 1
~/bin/getMergeChange.exp
~/bin/getPPFInfo.exp


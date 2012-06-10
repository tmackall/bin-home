#!/bin/bash
p4 dirs //release/linux-enablement/* | sort | perl -ne 's/\n//' -p | perl -ne 's/.*(\/\/.*)$/$1\n/' -p
p4 dirs //release/linux-enablement/* | sort | perl -ne 's/\n//' -p | perl -ne 's/.*\/(([0-9]|\.)+)$/$1\n/' -p


#!/bin/bash

google-drive-ocamlfuse /home/tmackall/google-drive
STATUS=$?
echo -e "\nGoogle Drive mount status: $STATUS"
exit $STATUS

#!/bin/bash

#
# used to generate an encrypted password
if [[ $# -ne 1 ]]; then
    echo -e "\nusage: $0 <password>\n"
    exit 2
fi
PASS="$1"

mkpasswd  -m sha-512 -S saltsalt -s <<< "$PASS"
exit 0

#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Usage : $0 <django database>"
    exit 1
fi
DATABASE=${1}
mysql -u root --password=dampob12  -e "CREATE DATABASE ${DATABASE};"

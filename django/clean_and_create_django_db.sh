#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Usage : $0 <django database>"
    exit 1
fi
DATABASE=${1}
#cd /home/tmackall/django/mackallHouse
LOC=$(pwd)
echo ${LOC}

TABLES=$(mysql -u root --password=dampob12  ${DATABASE}  -e 'show tables' | awk '{ print $1}' | grep -v '^Tables' )
 
for t in $TABLES
do
	echo "Deleting $t table from mackallHouse database..."
	mysql -u root --password=dampob1 ${DATABASE} -e "drop table $t"
done
python ${LOC}/manage.py syncdb

#!/bin/bash
cd ~/django/mackallHouse

TABLES=$(mysql -u root --password=dampob12  django_db  -e 'show tables' | awk '{ print $1}' | grep -v '^Tables' )
 
for t in $TABLES
do
	echo "Deleting $t table from mackallHouse database..."
	mysql -u root --password=dampob12  django_db -e "drop table $t"
done
python manage.py syncdb

#!/bin/bash
cd /home/tmackall/django_projects/mackallHouse

TABLES=$(mysql -u tmackall --password=tmackall  mackallHouse  -e 'show tables' | awk '{ print $1}' | grep -v '^Tables' )
 
for t in $TABLES
do
	echo "Deleting $t table from mackallHouse database..."
	mysql -u tmackall --password=tmackall  mackallHouse -e "drop table $t"
done
python manage.py syncdb

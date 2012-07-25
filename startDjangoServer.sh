#!/bin/sh
. $HOME/.bashrc
nohup /home/tmackall/django_projects/mackallHouse/manage.py runserver 192.168.1.23:8000 > /home/tmackall/django.log 2>&1 &
exit 0



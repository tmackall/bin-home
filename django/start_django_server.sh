#!/bin/bash
. $HOME/.bashrc
nohup /home/tmackall/django/mackallHouse/manage.py runserver 192.168.1.18:8000 > /home/tmackall/django.log 2>&1 &
exit 0



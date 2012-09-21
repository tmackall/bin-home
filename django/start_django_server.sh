#!/bin/bash
. $HOME/.bashrc
nohup /home/tmackall/django_projects/mackallHouse/manage.py runserver mackall:8000 > /home/tmackall/django.log 2>&1 &
exit 0



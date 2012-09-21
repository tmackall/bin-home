#!/bin/bash
. ~/.bashrc
if [ $# -ne 1 ]; then
    echo "Usage : $0 <app name>"
    exit 1
fi
python $DJANGO_HOME/bin/django-admin.py startproject ${1}
echo "Created Django project : ${1}"

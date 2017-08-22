#!/bin/bash
BASEDIR=$(bash get_basedir.sh)
cd $BASEDIR/mysite
python manage.py runserver

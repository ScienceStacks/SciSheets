#!/bin/bash
clear
# Runs the unit tests used in scisheets
cd mysite
echo "**********************************"
echo "*********** scisheets ***************"
echo "**********************************"
echo "*scisheets.helpers"
python manage.py test scisheets.helpers
echo "*scisheets.ui"
python manage.py test scisheets.ui
echo "*scisheets.plugins"
python manage.py test scisheets.plugins
scisheets/core/tt
echo "**********************************"
echo "*********** mysite ***************"
echo "**********************************"
python manage.py test mysite
echo "**********************************"
echo "*********** javascript ***************"
echo "**********************************"
cd mysite/static/js_test
qq

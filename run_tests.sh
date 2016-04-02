#!/bin/bash
clear
echo "**** Export does not work"
read -p "Press enter to continue..."
# Runs the unit tests used in scisheets
cd mysite
echo "**********************************"
echo "*********** scisheets ***************"
echo "**********************************"
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

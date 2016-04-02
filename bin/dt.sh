#!/bin/bash
# Run the python test in the django environment for scisheets
cd $HOME/SciSheets/mysite
python manage.py test scisheets.core.$1

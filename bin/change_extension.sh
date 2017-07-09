#!/bin/bash
BASEDIR=$(bash get_basedir.sh)
HELPERS=$BASEDIR/mysite/mysite/helpers
python $HELPERS/change_extension.py 

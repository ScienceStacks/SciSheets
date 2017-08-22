#!/bin/bash
# Checks if there are residual debug flags
BASEDIR=$(bash get_basedir.sh)

cd $BASEDIR/mysite/scisheets; ftg.sh "IGNORE_TEST" | grep True

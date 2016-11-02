#!/bin/bash
# Checks if there are residual debug flags
cd $HOME/SciSheets/mysite/scisheets; ftg.sh "IGNORE_TEST" | grep True

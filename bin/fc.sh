#!/bin/bash
# Finds the files that need to be changed
LIST="CodeGeneration Files Testing Tree CommonUtil FileVersion Database"
clear
for x in $LIST
do
  echo " "
  echo "*** $x ***"
  ft.sh $x *.py | grep -v "Binary" | grep -v "("
done

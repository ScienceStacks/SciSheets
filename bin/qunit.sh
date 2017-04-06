#!/bin/bash
# Command line test for qunit. Assumes installation in npm
if [ $# -eq 0 ]; then
  FFILE="tests.html"
else
  FFILE=$1
fi
echo $FFILE
node-qunit-phantomjs $FFILE

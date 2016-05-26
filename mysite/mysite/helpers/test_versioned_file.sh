#!/bin/bash
# Script used to examine state while testing versioend_file
echo "cat /tmp/versioned_file.txt"
cat /tmp/versioned_file.txt
echo
echo """Contents of /tmp/versioned_file/"
for ff in `ls /tmp/versioned_file`
do
echo "**$ff**"
cat /tmp/versioned_file/$ff
echo
done

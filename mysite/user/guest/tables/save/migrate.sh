#!/bin/bash
# Migrates tables to handle simple changes
cp *.pcl save
cp _*.pcl save
for f in *.pcl
do
  echo "***Processing $f"
  cat save/$f | sed 's/core\.util\./core.helpers./g' > $f
  diff $f /tmp/$f
done

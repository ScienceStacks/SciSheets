#!/bin/bash
# Checks out the desired branch
cd $HOME/SciSheets/mysite
SQLFILE="db.sqlite3"
rm -f /tmp/$SQLFILE
cp $SQLFILE /tmp
python manage.py migrate
if [ $? -ne 0 ]
then
  echo "Migration failed."
  cp /tmp/$SQLFILE .
  exit -1
fi
git checkout $1
if [ $? -ne 0 ]
then
  echo "Checkout failed."
  cp /tmp/$SQLFILE .
  exit -1
fi
echo "***Checkout successful***"
git branch

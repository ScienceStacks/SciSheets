#!/bin/bash
# Run this script from its directory
REPO_DIR=`pwd`
CONF_PATH=$REPO_DIR/aux_files/000-default.conf
SITE_NAME=mysite
SITE_DIR=$REPO_DIR/$SITE_NAME
APP_DIR=$SITE_DIR/$SITE_NAME
echo "REPO_DIR=$REPO_DIR"
echo "CONF_PATH=$CONF_PATH"
echo "SITE_NAME=$SITE_NAME"
echo "SITE_DIR=$SITE_DIR"
echo "APP_DIR=$APP_DIR"
cd $HOME/BaseStack/fabric_files
fab setup_django:conf_path=$CONF_PATH,app_dir=$APP_DIR
# Set up the site context. ADD TO FABFILE?
echo "************ Configuration *************"
cd $REPO_DIR
rm -rf $SITE_DIR
django-admin startproject mysite
git checkout mysite
cd $SITE_NAME
python manage.py migrate
# Set up permissions
cd $REPO_DIR
echo "Current direction is `pwd`"
chmod o+w $SITE_NAME
cd $SITE_NAME
chmod o+w db.sqlite3
cd $SITE_NAME
chmod o+w uploads
##########
bash apache_restart.sh

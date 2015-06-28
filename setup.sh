#!/bin/bash
# Run this script from its directory
REPO_DIR=`pwd`
CONF_PATH=$REPO_DIR/aux_files/000-default.conf
SITE_NAME=mysite
SITE_DIR=$REPO_DIR/$SITE_NAME
APP_DIR=$SITE_DIR/$SITE_NAME
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

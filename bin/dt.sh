#!/bin/bash
# Run the python test in the django environment for scisheets
# $1 - file with extension or python path
filename=`echo $1 | sed "s/.py//"`
cur_dir=`pwd`
cd $HOME/SciSheets/mysite
home_dir=`pwd`
null_str=""
rel_dir="${cur_dir/$home_dir/}"
py_path=`echo $rel_dir | sed "s/^\///"`
py_path=`echo $py_path | sed "s/\//./g"`
test_path=$py_path.$filename
echo "*** Testing $test_path"
python manage.py test $test_path

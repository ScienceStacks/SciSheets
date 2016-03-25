#!/bin/bash
# Runs one or more tests for files
# Argument is a specific test file (w/o extension) or none.

PY_PATH="scisheets.core."
TEST_LIST="test_api test_table_evaluator test_util test_column test_table"
TEST_LIST="${TEST_LIST} util.test_combinatoric_lists util.test_trinary"

function runTests {
for f in $@
do
  echo ""
  echo "** $f **"
  pushd $HOME/SciSheets/mysite
  python manage.py test ${PY_PATH}${f}
  popd
done
}


# Main code

FILE_PATH="scisheets.core."

if [ $# -eq 0 ]; then
  runTests ${TEST_LIST}
else
  runTests $1
fi

#!/bin/bash

function runTests {
for f in test_*.py
do
  echo ""
  echo "** $f **"
  python $f
done
}

runTests
cd util
runTests

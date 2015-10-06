#!/bin/bash
# Prepares the test file and run the tests.

SITE=$HOME/SciSheets/mysite/mysite
cp $SITE/templates/scitable.html test1.html
sed 's/.{% static "/"\/home\/ubuntu\/SciSheets\/mysite\/mysite\/static\//' <test1.html >test2.html
sed 's/ %}.//' <test2.html >test3.html
sed '/table_setup.js/r insert.html' < test3.html > test4.html
sed '/load static from/s/^.*$//' < test4.html > test.html
mv test?.html /tmp
bash qunit.sh test.html

"""
Tests for YUI DataTable renderings.
"""

from mysite import settings
from mysite.helpers.versioned_file import VersionedFile
import scisheets.core.helpers.api_util as api_util
from scisheets.core.column import Column
from scisheets.core.helpers.api_util  \
    import readObjectFromFile, writeObjectToFile
from scisheets.core.helpers.serialize_deserialize import serialize,  \
    deserialize
from scisheets.core.helpers_test import TEST_DIR
import dt_table as dt
from django.test import TestCase  # Provides mocks
import json
import numpy as np
import os
import sys


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
# The following has unequal length columns and NaN
COMPLEX_DATA1 = [[3.2, 4.5, np.NaN], [10, 20, 30], [100, 200, 300], ['a', 'b']]
COMPLEX_DATA2 = [[[], [1], [1, 2]], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
NCOL = 4
NROW = 3
TABLE_NAME = "MY TABLE"
CUR_DIR = os.path.dirname(__file__)
TESTFILE2 = "testcase_2.scish"
TESTFILE3 = "testcase_3.scish"

IGNORE_TESTS = False


# Ensure that tested module is accessible in debugger
sys.path.append(CUR_DIR)


class TestAuxFunctions(TestCase):

  def _testMakeJSDataStr(self, column_data):
    js_data = dt.makeJSData(column_data)
    self.assertTrue(isinstance(js_data, list))
    num_rows = 1
    if isinstance(column_data[0], list):
      num_rows = len(column_data[0])
    for c in range(len(column_data)):
      for r in range(num_rows):
        if isinstance(column_data[c], list):
          value = column_data[c][r]
        else:
          value = column_data[c]
        self.assertEqual(str(value),
                         js_data[r][c])

  def testMakeJSDataStr(self):
    if IGNORE_TESTS:
      return
    self._testMakeJSDataStr(DATA)
    self._testMakeJSDataStr(DATA_STRING)

  def testMakeJSDataComplex1(self):
    if IGNORE_TESTS:
      return
    js_data = dt.makeJSData(COMPLEX_DATA1)
    row3 = js_data[2]
    self.assertEqual(row3[0], "")
    self.assertEqual(row3[3], "")

  def testMakeJSDataComplex2(self):
    if IGNORE_TESTS:
      return
    js_data = dt.makeJSData(COMPLEX_DATA2)
    row3 = js_data[2]
    self.assertEqual(row3[2], "300")
    self.assertEqual(row3[0], str(COMPLEX_DATA2[0][2]))

  def testSpecificCases(self):
    """
    Inputs to test cases are stored in pcl files.
    """
    if IGNORE_TESTS:
      return
    files = ["test_dt_table_1.scish"]
    # Tests are functions that take result as an argument and return a bool
    tests = [ (lambda r: r[1]['Col_1'] == `0.5`)]
    iterations = range(len(files))
    for idx in iterations:
       path = os.path.join(CUR_DIR, files[idx])
       inputs = api_util.readObjectFromFile(path)
       column_names = inputs[0]
       data = inputs[1]
       result = dt.makeJSData(data)
       self.assertEqual(len(result), len(data[0]))


class TestDTTable(TestCase):

  def setUp(self):
    self.table = dt.DTTable.createRandomTable(TABLE_NAME,
        NROW, NCOL)

  # TODO: Do something better with this test
  def testRender(self):
    if IGNORE_TESTS:
      return
    Col_0 = self.table.getColumns()[1]
    Col_0.setFormula("Col_1 = 'x'")
    self.table.evaluate(user_directory=TEST_DIR)
    html = self.table.render()
    self.assertIsNotNone(html)
    column_hierarchy = ['name: "row"', 'label: "row"', 'children: [']
    response_schema = "row"
    data_source = "[['1', '"
    expecteds = [response_schema, data_source]
    expecteds.extend(column_hierarchy)
    for expected in expecteds:
      self.assertTrue(expected in html)

  def testHierarchicalRender(self):
    if IGNORE_TESTS:
      return
    table = dt.DTTable.createRandomHierarchicalTable(TABLE_NAME,
        NROW, NCOL, prob_child=0.6, table_cls=dt.DTTable)
    html = table.render()
    self.assertIsNotNone(html)
    tests = [isinstance(nl, dt.DTTable) for nl in table.getNonLeaves()]
    self.assertTrue(all(tests))
    tests = [isinstance(l, Column) for l in table.getLeaves()]
    self.assertTrue(all(tests))

  def testRenderingListData(self):
    # set up the test table
    if IGNORE_TESTS:
      return
    table_filepath = os.path.join(TEST_DIR, TESTFILE2)
    table = readObjectFromFile(table_filepath, verify=False)
    versioned_file = VersionedFile(table_filepath, TEST_DIR, 0)
    table.setVersionedFile(versioned_file)
    html = table.render()

  def testSerializeDeserialize(self):
    if IGNORE_TESTS:
      return
    json_str = serialize(self.table)
    new_table = deserialize(json_str)
    self.assertTrue(self.table.isEquivalent(new_table))

  def testMakeAnnotatedDepthFirstTreeRepresentation(self):
    if IGNORE_TESTS:
      return
    result = self.table._makeAnnotatedDepthFirstTreeRepresentation()
    pass


if __name__ == '__main__':
    unittest.man()

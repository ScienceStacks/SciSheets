"""
Tests for YUI DataTable renderings.
"""

from mysite import settings
from mysite.helpers.versioned_file import VersionedFile
import scisheets.core.helpers.api_util as api_util
from scisheets.core.helpers.api_util  \
    import readObjectFromFile, writeObjectToFile
from scisheets.core.helpers.serialize_deserialize import serialize,  \
    deserialize
from scisheets.core.helpers_test import TEST_DIR
import dt_table as dt
from django.test import TestCase  # Provides mocks
import ast
import json
import os
import pickle
import sys


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
COMPLEX_DATA = [[[], [1], [1, 2]], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
NCOL = 4
NROW = 3
TABLE_NAME = "MY TABLE"
CUR_DIR = os.path.dirname(__file__)
TESTFILE2 = "testcase_2.sci"
TESTFILE3 = "testcase_3.sci"


# Ensure that tested module is accessible in debugger
sys.path.append(CUR_DIR)


class TestAuxFunctions(TestCase):

  def _testMakeJSONStr(self, column_names, column_data, data_type):
    json_str = dt.makeJSON(column_names, column_data)
    converted = json.loads(json_str.replace("`", '"'))
    self.assertTrue(isinstance(converted, list))
    self.assertEqual(len(converted[0]), len(column_names))
    for n in range(len(converted)):
      self.assertTrue(isinstance(converted[n], dict))

  def testMakeJSONStr(self):
    self._testMakeJSONStr(COLUMN_NAMES, DATA, list)
    self._testMakeJSONStr(COLUMN_NAMES, DATA_STRING, str)

  def testMakeJSONComplex(self):
    json_str = dt.makeJSON(COLUMN_NAMES, COMPLEX_DATA)
    out_list = eval(json_str)
    self.assertTrue(out_list[0]['A'], '[]')
    self.assertTrue(out_list[1]['A'], '[1]')
    self.assertTrue(out_list[2]['A'], '[1, 2]')

  def testSpecificCases(self):
    """
    Inputs to test cases are stored in pcl files.
    """
    files = ["test_dt_table_1.sci"]
    # Tests are functions that take result as an argument and return a bool
    tests = [ (lambda r: r[1]['Col_1'] == `0.5`)]
    iterations = range(len(files))
    for idx in iterations:
       path = os.path.join(CUR_DIR, files[idx])
       inputs = api_util.readObjectFromFile(path)
       column_names = inputs[0]
       data = inputs[1]
       result = dt.makeJSON(column_names, data)
       cleaned_result = result.replace("`", "'")
       result_list = ast.literal_eval(cleaned_result)
       test = tests[idx]
       self.assertTrue(test(result_list))


class TestDTTable(TestCase):

  def setUp(self):
    self.table = dt.DTTable.createRandomTable(TABLE_NAME,
        NROW, NCOL)

  # TODO: Do something better with this test
  def testRender(self):
    Col_0 = self.table.getColumns()[1]
    Col_0.setFormula("Col_1 = 'x'")
    self.table.evaluate(user_directory=TEST_DIR)
    html = self.table.render()
    self.assertIsNotNone(html)

  def testRenderingListData(self):
    # set up the test table
    table_filepath = os.path.join(TEST_DIR, TESTFILE2)
    table = readObjectFromFile(table_filepath, verify=False)
    versioned_file = VersionedFile(table_filepath, TEST_DIR, 0)
    table.setVersionedFile(versioned_file)
    html = table.render()

  def testSerializeDeserialize(self):
    json_str = serialize(self.table)
    new_table = deserialize(json_str)
    self.assertTrue(self.table.isEquivalent(new_table))


if __name__ == '__main__':
    unittest.man()

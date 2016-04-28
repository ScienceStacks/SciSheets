"""
Tests importExcel
"""

from importExcel import importExcel, importExcelToDataframe
from scisheets.core import api as api
from scisheets.core import helpers_test as ht
import os
import pandas as pd
import unittest

TEST_FILE = os.path.join(ht.TEST_DIR, "excel_read.xlsx")
COLUMN_NAMES = ['v1', 'v2']
DATA = {'v1': [11, 22, 33], 'v2': [111, 222, 333]}


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestImportExcel(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)
    self.api = api.APIFormulas(self.table)

  def testBadPath(self):
    b = False
    error = None
    try:
      importExcel(self.api, "badpath.csv")
    except Exception as e:
      error = e
      b = isinstance(e, IOError) or isinstance(e, ValueError)
    self.assertTrue(b)

  def testBadColumn(self):
    with self.assertRaises(ValueError):
      importExcel(self.api, TEST_FILE, ['w'])

  def _testImportColumns(self, names=None, worksheet=None):
    imported_names = importExcel(self.api, 
                                TEST_FILE, 
                                worksheet=worksheet,
                                names=names)
    if worksheet is None:
      worksheet = 'Sheet1'
    if names is None:
      names = COLUMN_NAMES
    self.assertTrue(imported_names == names)
    for name in names:
      self.assertTrue(self.api._table.isColumnPresent(name))
      column = self.api._table.columnFromName(name)
      imported_values = column.getCells()
      expected_values = DATA[name]
      self.assertTrue(imported_values == expected_values)

  def testImportColumns(self):
    self._testImportColumns()
    self._testImportColumns(names=['v1'])
    self._testImportColumns(worksheet='Sheet1')
    self._testImportColumns(worksheet='Sheet1', names=['v2'])
    

if __name__ == '__main__':
  unittest.main()

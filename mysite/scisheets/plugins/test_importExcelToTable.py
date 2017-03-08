"""
Tests importExcelToTable
"""

from importExcelToTable import importExcelToTable,  \
    _importExcelToDataframe
from scisheets.core import api as api
from scisheets.core import helpers_test as ht
import os
import pandas as pd
import unittest

TEST_FILE1 = os.path.join(ht.TEST_DIR, "excel_read.xlsx")
TEST_FILE2 = os.path.join(ht.TEST_DIR, "test_importExcelToTable_1.xlsx")
TEST_FILE3 = "test_importExcelToTable_2"
COLUMN_NAMES = ['v1', 'v2']
DATA = {'v1': [11, 22, 33], 'v2': [111, 222, 333]}


#############################
# Tests
#############################
# TODO: Tests for column_position argument
# pylint: disable=W0212,C0111,R0904
class TestImportExcel(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)
    self.api = api.APIFormulas(self.table)

  def testBadPath(self):
    b = False
    error = None
    try:
      importExcelToTable(self.api, "badpath.csv")
    except Exception as e:
      error = e
      b = isinstance(e, IOError) or isinstance(e, ValueError)
    self.assertTrue(b)

  def testBadColumn(self):
    with self.assertRaises(ValueError):
      importExcelToTable(self.api, TEST_FILE1, ['w'])

  def _testImportTable(self, names=None, worksheet=None, 
      filename=TEST_FILE1):
    table = self.api.getTable()
    old_table = table.copy()
    for col_pos in [ht.COLUMN1, ht.COLUMN5, None]:
      table = old_table
      self.api._table = table
      column_position = col_pos
      imported_names = importExcelToTable(self.api,
          filename, worksheet=worksheet, names=names,
          column_position=column_position)
      if worksheet is None:
        worksheet = 'Sheet1'
      if names is None:
        names = COLUMN_NAMES
      self.assertTrue(imported_names == names)
      indicies = range(len(names))
      pairs = zip(names, indicies)
      for name, index in pairs:
        self.assertTrue(table.isColumnPresent(name))
        column = table.columnFromName(name, is_relative=True)
        if column is None:
          import pdb; pdb.set_trace()
        imported_values = column.getCells()
        expected_values = DATA[name]
        self.assertTrue(imported_values == expected_values)
        # Check the column position
        old_column = old_table.columnFromName(name, is_relative=True)
        if old_column is not None:
          expected_index = old_table.indexFromColumn(old_column)
        else:
          expected_index = old_table.numColumns() + index
        column_index = table.indexFromColumn(column)
        if column_index != expected_index:
          import pdb; pdb.set_trace()
        self.assertEqual(column_index, expected_index)

  def testImportTable(self):
    return
    self._testImportTable()
    self._testImportTable(names=['v1'])
    self._testImportTable(worksheet='Sheet1')
    self._testImportTable(worksheet='Sheet1', names=['v2'])

  def testImportTableWithMissingData(self):
    names = ['ItemRelation', 'AccountRelation', 'QuantityAmount', 
        'Amount', 'FromDate', 'ToDate']
    worksheet = 'Sheet1'
    filename = TEST_FILE2
    table = self.api.getTable()
    imported_names = importExcelToTable(self.api,
        filename, worksheet=worksheet, names=names)
    self.assertTrue(imported_names == names)
    

if __name__ == '__main__':
  unittest.main()

"""
Tests exportExcelToTable
"""

from exportTableToExcel import exportTableToExcel,  \
    _exportDataframeToExcel
from importExcelToTable import importExcelToTable,  \
    _importExcelToDataframe
from scisheets.core import api as api
from scisheets.core import helpers_test as ht
import os
import pandas as pd
import unittest

TEST_FILE = os.path.join(ht.TEST_DIR, "excel_write.xlsx")


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestImportExcel(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)
    self.api = api.APIFormulas(self.table)
    self.df = self._createDataframe()
    self.columns = self.df.columns

  def _createDataframe(self):
    df = pd.DataFrame()
    table = self.api.getTable()
    for column in table.getDataColumns():
      name = column.getName()
      df[name] = column.getCells()
    return df

  def testBadPath(self):
    return
    b = False
    error = None
    try:
      df = pd.DataFrame()
      exportTableToExcel(self.api, "this/badpath.csv", df)
    except Exception as e:
      error = e
      import pdb; pdb.set_trace()
      b = isinstance(e, IOError) or isinstance(e, ValueError)
    self.assertTrue(b)

  def testBadColumn(self):
    with self.assertRaises(ValueError):
      exportTableToExcel(self.api, TEST_FILE, self.df, ['w'])

  def _compareExportedDataframe(self, worksheet, columns):
    excel_df = _importExcelToDataframe(TEST_FILE, 
                                       worksheet=worksheet) 
    self.assertEqual(len(excel_df.columns), len(columns))
    for name in columns:
      b = list(excel_df[name]) ==  list(self.df[name])
      if not b:
        import pdb; pdb.set_trace()
      self.assertTrue(b)

  def _testExportDataframe(self, worksheet=None):
    _exportDataframeToExcel(self.df, TEST_FILE, worksheet=worksheet)
    self._compareExportedDataframe(worksheet, self.df.columns)

  def testExportDataframe(self):
    self._testExportDataframe()
    self._testExportDataframe(worksheet='Sheet1')

  def _testExportTable(self, columns=None, worksheet=None):
    exportTableToExcel(self.api, 
                       TEST_FILE, 
                       worksheet=worksheet, 
                       columns=columns)
    if columns is None:
      columns = self.columns
    if worksheet is None:
      expected_worksheet = 'Sheet1'
    self._compareExportedDataframe(worksheet, columns)

  def testExportTable(self):
    self._testExportTable()
    self._testExportTable(columns=['DUMMY1_COLUMN'])
    self._testExportTable(worksheet='Sheet1')
    self._testExportTable(worksheet='Sheet1', 
        columns=['DUMMY1_COLUMN', 'DUMMY2_COLUMN'])
    

if __name__ == '__main__':
  unittest.main()

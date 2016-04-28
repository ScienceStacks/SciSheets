"""
Tests exportExcel
"""

from exportExcel import exportExcel
from importExcel import importExcel, importExcelToDataframe
from scisheets.core import api as api
from scisheets.core import helpers_test as ht
import os
import pandas as pd
import unittest

TEST_FILE = os.path.join(ht.TEST_DIR, "excel_write.xlsx")
DATA = {'va': [11, 22, 33], 'vb': [111, 222, 333]}
COLUMN_NAMES = DATA.keys()


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestImportExcel(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)
    self.api = api.APIFormulas(self.table)

  def testBadPath(self):
    return
    b = False
    error = None
    try:
      df = pd.DataFrame()
      exportExcel(self.api, "this/badpath.csv", df)
    except Exception as e:
      error = e
      import pdb; pdb.set_trace()
      b = isinstance(e, IOError) or isinstance(e, ValueError)
    self.assertTrue(b)

  def testBadColumn(self):
    df = pd.DataFrame()
    with self.assertRaises(ValueError):
      exportExcel(self.api, TEST_FILE, df, ['w'])

  def _testExportColumns(self, names=None, worksheet=None):
    df = pd.DataFrame()
    for key in DATA.keys():
      df[key] = DATA[key]
    exportExcel(self.api, TEST_FILE, df, worksheet=worksheet, names=names)
    if worksheet is None:
      expected_worksheet = 'Sheet1'
    if names is None:
      expected_names = COLUMN_NAMES
    excel_df = importExcelToDataframe(TEST_FILE, worksheet=worksheet) 
    self.assertEqual(len(excel_df.columns),
                     len(df.columns))
    for name in COLUMN_NAMES:
      self.assertTrue(list(excel_df[name]) ==  list(df[name]))

  def testExportColumns(self):
    self._testExportColumns()
    self._testExportColumns(names=['v1'])
    self._testExportColumns(worksheet='Sheet1')
    self._testExportColumns(worksheet='Sheet1', names=['v2'])
    

if __name__ == '__main__':
  unittest.main()

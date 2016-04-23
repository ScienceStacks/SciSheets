'''
Tests for API excel utilities.
 '''

from ...core import helpers_test as ht
import api_util_excel
import numpy as np
import os
import unittest

TEST_WRITE_FILE = os.path.join(ht.TEST_DIR, "excel_write.xlsx")
TEST_READ_FILE = os.path.join(ht.TEST_DIR, "excel_read.xlsx")
ARRAY_INT = np.array(range(4))
ARRAY_INT_LONG = np.array(range(5))
ARRAY_FLOAT = np.array([0.01*x for x in range(4)])


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestAPIUtilExcel(unittest.TestCase):

  def setUp(self):
    self.excel_w = api_util_excel.APIUtilExcel(TEST_WRITE_FILE)
    self.excel_r = api_util_excel.APIUtilExcel(TEST_READ_FILE)

  def testOpenWrite(self):
    self.excel_w.openWrite()
    self.assertIsNotNone(self.excel_w._workbook)
    self.assertEqual(self.excel_w._filemode, api_util_excel.WRITE)

  def testOpenRead(self):
    self.excel_r.openRead()
    self.assertIsNotNone(self.excel_r._workbook)
    self.assertEqual(self.excel_r._filemode, api_util_excel.READ)

  def testSetWorksheet(self):
    self.excel_r.openRead()
    self.excel_r.setWorksheet('Sheet1')
    self.assertIsNotNone(self.excel_r._worksheet)
    with self.assertRaises(KeyError):
      self.excel_r.setWorksheet('DummySheet')
    self.excel_w.openWrite()
    self.excel_w.setWorksheet('Sheet1')
    self.assertIsNotNone(self.excel_w._worksheet)
    self.excel_w.setWorksheet('DummySheet')
    self.assertIsNotNone(self.excel_w._worksheet)

  def _testReadColumn(self, columnid, has_header=False, sheet='Sheet1', is_valid=True):
    expected_column = ['v1', 11, 22, 33]
    if has_header:
      expected_header = expected_column[0]
      expected_var = expected_column[1:]
    else:
      expected_header = None
      expected_var = [str(x) for x in expected_column]
    self.excel_r.openRead()
    self.excel_r.setWorksheet(sheet)
    var, header = self.excel_r.readColumn(columnid, has_header)
    if is_valid:
      self.assertEqual(expected_header, header)
      self.assertTrue(expected_var == var.tolist())
    else:
      self.assertNotEqual(expected_header, header)
      self.assertFalse(expected_var == var.tolist())

  def testReadColumn(self):
    self._testReadColumn(1, has_header=False)
    self._testReadColumn(1, has_header=True)
    self._testReadColumn('A', has_header=False)
    self._testReadColumn('A', has_header=True)
    self._testReadColumn(2, has_header=True, is_valid=False)
    


if __name__ == '__main__':
  unittest.main()

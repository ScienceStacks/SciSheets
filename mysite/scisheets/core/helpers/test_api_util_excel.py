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


if __name__ == '__main__':
  unittest.main()

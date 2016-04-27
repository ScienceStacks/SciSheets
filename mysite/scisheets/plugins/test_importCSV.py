"""
Tests importCSV
"""

from importCSV import importCSV
from scisheets.core import api as api
from scisheets.core import helpers_test as ht
import os
import pandas as pd
import unittest



#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestAPI(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)
    self.api = api.APIFormulas(self.table)

  def testImportCSV(self):
    filename = "test_importCSV.csv"
    filepath = os.path.join(ht.TEST_DIR, filename)
    names  = ["x", "y", "z"]
    data = [ names, [1, 10.0, "aa"], [2, 20.0, "bb"]]
    data_len = len(data) - 1
    data_idx = range(1, len(data))
    fd = open(filepath, "w")
    for line_as_list in data:
      str_list = [str(x) for x in line_as_list]
      line = "%s\n" % (','.join(str_list))
      fd.write(line)
    fd.close()
    try:
      importCSV(self.api, "badpath.csv")
    except Exception as e:
      b = isinstance(e, IOError) or isinstance(e, ValueError)
      self.assertTrue(b)
    with self.assertRaises(KeyError):
      importCSV(self.api, filepath, ['w'])
    column_list = list(names)
    imported_names = importCSV(self.api, filepath, names=column_list)
    self.assertTrue(imported_names == column_list)
    for idx in range(len(column_list)):
      name = names[idx]
      self.assertTrue(self.api._table.isColumnPresent(name))
      column = self.api._table.columnFromName(name)
      values = column.getCells()[:data_len]
      expected_list = [data[n][idx] for n in range(1, len(data))]
      self.assertTrue(values == expected_list)

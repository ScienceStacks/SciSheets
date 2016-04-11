'''Tests for formulas API'''

from api import API, APIFormulas, APIPlugin
import helpers_test as ht
import table_evaluator as te
import numpy as np
import os
from helpers.trinary import Trinary
import unittest

COLUMN1 = "Col_1"
COLUMN2 = "Col_2"
TRUTH_COLUMNS = ['A', 'B']
COLUMN1_VALUES = range(10)

#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestAPI(unittest.TestCase):

  def setUp(self):
    self.api = API()
    self.api._table = ht.createTable("test", column_name=COLUMN1)
    self.column1 = self.api._table.columnFromName(COLUMN1)
    self.column1.addCells(COLUMN1_VALUES, replace=True)

  def testGetColumnValues(self):
    values = self.api.getColumnValues(COLUMN1)
    self.assertTrue(all(values == COLUMN1_VALUES))

  def testSetColumnValues(self):
    new_column1_values = list(COLUMN1_VALUES)
    new_column1_values.extend(range(5))
    self.api.setColumnValues(COLUMN1, new_column1_values)
    values = self.api.getColumnValues(COLUMN1)
    self.assertTrue(all(values == np.array(new_column1_values)))
    

# pylint: disable=W0212,C0111,R0904
class TestAPIFormulas(unittest.TestCase):

  def setUp(self):
    table = ht.createTable("test", column_name=COLUMN1)
    self.api = APIFormulas(table)

  def testGetValidatedColumn(self):
    column = self.api._getColumn(COLUMN1)
    self.assertEqual(column.getName(), COLUMN1)

  def _createColumn(self):
    self.api.createColumn(COLUMN2)
    return self.api._getColumn(COLUMN2)

  def testCreateColumn(self):
    column = self._createColumn()
    self.assertEqual(column.getName(), COLUMN2)

  def testDeleteColumn(self):
    _ = self._createColumn()
    self.api.deleteColumn(COLUMN2)
    is_absent = all([c.getName() != COLUMN2  \
        for c in self.api._table.getColumns()])
    self.assertTrue(is_absent)
    _ = self._createColumn()
    self.api.deleteColumn(2)
    is_absent = all([c.getName() != COLUMN2  \
        for c in self.api._table.getColumns()])
    self.assertTrue(is_absent)

  def testParam(self):
    p1 = self.api.param(COLUMN1)
    self.assertEqual(p1, 0)
    p2 = self.api.param(COLUMN1, row_num=2)
    self.assertEqual(p2, 1)

  def _createTruthTable(self):
    return
    self.api.deleteColumn(COLUMN1)
    self.api.createTruthTable(TRUTH_COLUMNS, only_boolean = True)

  def testCreateTruthTable(self):
    return
    self._createTruthTable()
    for n in range(len(TRUTH_COLUMNS)):
      self.assertTrue(any([c.getName() == TRUTH_COLUMNS[n]
          for c in self.api._table.getColumns()]))

  def testCreateTrinary(self):
    return
    self._createTruthTable()
    for n in range(len(TRUTH_COLUMNS)):
      column = self.api._table.columnFromName(TRUTH_COLUMNS[n])
      trinary = self.api.createTrinary(column.getCells())
      new_trinary = -trinary
      self.assertTrue(isinstance(new_trinary, Trinary))

  def testImportCSV(self):
    filename = "test_api.csv"
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
      self.api.importCSV("badpath.csv")
    except Exception as e:
      b = isinstance(e, IOError) or isinstance(e, ValueError)
      self.assertTrue(b)
    with self.assertRaises(ValueError):
      self.api.importCSV(filepath, ['w'])
    column_list = list(names)
    imported_names = self.api.importCSV(filepath, column_names=column_list)
    self.assertTrue(imported_names == column_list)
    for idx in range(len(column_list)):
      name = names[idx]
      self.assertTrue(self.api._table.isColumnPresent(name))
      column = self.api._table.columnFromName(name)
      values = column.getCells()[:data_len]
      expected_list = [data[n][idx] for n in range(1, len(data))]
      self.assertTrue(values == expected_list)
    

# pylint: disable=W0212,C0111,R0904
class TestAPIPlugin(unittest.TestCase):

  def setUp(self):
    table = ht.createTable("test", column_name=COLUMN1)
    self.api = APIPlugin(table.getFilepath())
    self.api.initialize()


if __name__ == '__main__':
  unittest.main()

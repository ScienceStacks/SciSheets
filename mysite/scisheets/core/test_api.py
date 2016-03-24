'''Tests for formulas API'''

from api import API, APIFormulas, APIAdmin
import helpers_test as ht
import numpy as np
from util.trinary import Trinary
import unittest

COLUMN1 = "Col_1"
COLUMN2 = "Col_2"
TRUTH_COLUMNS = ['A', 'B']

#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestAPIFormulas(unittest.TestCase):

  def setUp(self):
    self.table = ht.createTable("test", column_name=COLUMN1)
    self.api = APIFormulas(self.table)

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
        for c in self.table.getColumns()])
    self.assertTrue(is_absent)
    _ = self._createColumn()
    self.api.deleteColumn(2)
    is_absent = all([c.getName() != COLUMN2  \
        for c in self.table.getColumns()])
    self.assertTrue(is_absent)

  def testParam(self):
    p1 = self.api.param(COLUMN1)
    self.assertEqual(p1, 0)
    p2 = self.api.param(COLUMN1, row_num=2)
    self.assertEqual(p2, 1)

  def _createTruthTable(self):
    self.api.deleteColumn(COLUMN1)
    self.api.createTruthTable(TRUTH_COLUMNS, only_boolean = True)

  def testCreateTruthTable(self):
    self._createTruthTable()
    for n in range(len(TRUTH_COLUMNS)):
      self.assertTrue(any([c.getName() == TRUTH_COLUMNS[n]
          for c in self.table.getColumns()]))

  def testCreateTrinary(self):
    self._createTruthTable()
    for n in range(len(TRUTH_COLUMNS)):
      column = self.table.columnFromName(TRUTH_COLUMNS[n])
      trinary = self.api.createTrinary(column.getCells())
      new_trinary = -trinary
      self.assertTrue(isinstance(new_trinary, Trinary))

    

if __name__ == '__main__':
  unittest.main()

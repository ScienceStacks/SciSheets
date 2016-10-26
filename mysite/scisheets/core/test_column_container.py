'''Tests for ColumnContainer'''

from column_container import ColumnContainer
from table import Table
import column as cl
import errors as er
from helpers_test import createTable
import numpy as np
import unittest


# Constants
COLUMN = "DUMMY_COLUMN"
COLUMN1 = "DUMMY1_COLUMN"
COLUMN2 = "DUMMY2_COLUMN"
COLUMN3 = "DUMMY3_COLUMN"
COLUMN4 = "DUMMY4_COLUMN"
COLUMN5 = "DUMMY5_COLUMN"
SUBTABLE = "Subtable"
COLUMN2_INDEX = 1
TABLE_NAME = "DUMMY_TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
FORMULA = "A+B"
COLUMN1_CELLS = ["one", "two", "three"]
COLUMN2_CELLS = [10.1, 20.0, 30.0]
COLUMN5_CELLS = [100.0, 200.0, 300.0]

IGNORE_TEST = False


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestColumnContainer(unittest.TestCase):

  def setUp(self):
    self.table = createTable(TABLE_NAME)
    column1 = cl.Column(COLUMN1)
    column1.addCells(COLUMN1_CELLS)
    self.table.addColumn(column1)
    column2 = cl.Column(COLUMN2)
    column2.addCells(COLUMN2_CELLS)
    error = self.table.addColumn(column2)
    if error is not None:
      import pdb; pdb.set_trace()
    self.column5 = cl.Column(COLUMN5)
    self.column5.addCells(COLUMN5_CELLS)
    self.table.addColumn(self.column5)
    self.columns = self.table.getColumns()
    self.subtable = Table(SUBTABLE)
    self.table.addChild(self.subtable)
    self.subtable_column = self.subtable.getChildAtPosition(0)
    self.subtable_column_name = 'row'

  def testColumnFromIndex(self):
    if IGNORE_TEST:
      return
    column = self.table.columnFromIndex(0)
    self.assertEqual(column.getName(), 'row')
    index = self.table.numColumns()
    with self.assertRaises(ValueError):
      self.table.columnFromIndex(index)

  def testColumnFromName(self):
    if IGNORE_TEST:
      return
    global_name = self.table.createGlobalName(self.subtable_column)
    column = self.table.columnFromName(global_name, is_relative=False)
    self.assertTrue(column.isEquivalent(self.subtable_column))
    column = self.table.columnFromName(COLUMN5, is_relative=True)
    self.assertTrue(column.isEquivalent(self.column5))
    self.assertIsNone(self.table.columnFromName(SUBTABLE, is_relative=True))

  def testGetColumnNames(self):
    if IGNORE_TEST:
      return
    names = self.subtable.getColumnNames()
    self.assertEqual(names, [self.subtable_column.getName()])
    names = self.table.getColumnNames()
    self.assertTrue(not SUBTABLE in names)

  def testGetColumns(self):
    columns = self.subtable.getColumns()
    self.assertEqual(columns, [self.subtable_column])
    table_columns = self.table.getColumns()
    self.assertTrue(not self.subtable in table_columns)
    columns = self.table.getColumns(is_recursive=False)
    self.assertEqual(len(columns) + 1, len(table_columns))
    

if __name__ == '__main__':
  unittest.main()

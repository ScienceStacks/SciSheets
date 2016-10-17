'''Tests for ColumnContainer'''

from column_container import ColumnContainer
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
COLUMN2_INDEX = 1
TABLE_NAME = "DUMMY_TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
FORMULA = "A+B"
COLUMN1_CELLS = ["one", "two", "three"]
COLUMN2_CELLS = [10.1, 20.0, 30.0]
COLUMN5_CELLS = [100.0, 200.0, 300.0]


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
    self.table.addColumn(column2)
    column5 = cl.Column(COLUMN5)
    column5.addCells(COLUMN5_CELLS)
    self.table.addColumn(column5)
    self.columns = self.table.getColumns()

  def testColumnFromIndex(self):
    column = self.table.columnFromIndex(0)
    self.assertEqual(column.getName(), 'row')

  def testGetCell(self):
    self.assertEqual(self.table.getCell(0, 1),
                     COLUMN1_CELLS[0])

  def testInsertColumn(self):
    new_column_name = "NEW_COLUMN"
    index = 1
    new_column = cl.Column(new_column_name)
    self.table.insertColumn(new_column, index)
    self.assertEqual(self.table.getColumns()[index].getName(),
        new_column_name)
    newer_column_name = "NEWER_COLUMN"
    newer_column = cl.Column(newer_column_name)
    index = len(self.table.getColumns())
    self.table.insertColumn(newer_column)
    self.assertEqual(self.table.getColumns()[index].getName(),
        newer_column_name)

  def testMoveColumn1(self):
    # Move column 2 to be after column 0
    dest_idx = 0
    column2 = self.table.columnFromName(COLUMN2)
    self.table.moveColumn(column2, dest_idx)
    self.assertEqual(self.table.getColumns()[dest_idx+1].getName(), COLUMN2)

  def testNumColumns(self):
    self.assertEqual(self.table.numColumns(), 4)

  def testRemoveColumn(self):
    num_col = self.table.numColumns()
    column = self.table.getColumns()[1]
    self.table.removeColumn(column)
    self.assertEqual(self.table.numColumns(), num_col - 1)

  def testSetName(self):
    self.assertIsNone(self.table.setName("newTable"))
    self.assertIsNotNone(self.table.setName("new Table"))

if __name__ == '__main__':
  unittest.main()

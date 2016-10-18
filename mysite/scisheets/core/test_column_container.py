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
    self.table.addColumn(column2)
    self.column5 = cl.Column(COLUMN5)
    self.column5.addCells(COLUMN5_CELLS)
    self.table.addColumn(self.column5)
    self.columns = self.table.getColumns()
    self.subtable = Table(SUBTABLE)
    self.table.addChild(self.subtable)
    self.subtable_column = self.subtable.getColumns()[0]

  def testColumnFromIndex(self):
    if IGNORE_TEST:
      return
    column = self.table.columnFromIndex(0)
    self.assertEqual(column.getName(), 'row')
    index = self.table.numColumns()
    with self.assertRaises(ValueError):
      self.table.columnFromIndex(index)

  def testCreateFullName(self):
    if IGNORE_TEST:
      return
    full_name = self.table._createFullName(self.column5)
    expected_name = ".".join([self.table.getName(), self.column5.getName()])
    self.assertEqual(full_name, expected_name)
    full_name = self.table._createFullName(self.subtable_column)
    expected_name = ".".join([self.table.getName(), SUBTABLE, 
        self.subtable_column.getName()])
    self.assertEqual(full_name, expected_name)

  def testRelativeNameToFullName(self):
    if IGNORE_TEST:
      return
    full_name = self.table._relativeNameToFullName(COLUMN5, is_relative=True)
    expected_name = ".".join([self.table.getName(), self.column5.getName()])
    self.assertEqual(full_name, expected_name)
    full_name = self.table._relativeNameToFullName(full_name, is_relative=False)
    expected_name = ".".join([self.table.getName(), self.column5.getName()])

  def testChildFromName(self):
    if IGNORE_TEST:
      return
    full_name = self.table._createFullName(self.subtable_column)
    column = self.table.childFromName(full_name, is_relative=False)
    self.assertTrue(column.isEquivalent(self.subtable_column))
    subtable = self.table.childFromName(SUBTABLE, is_relative=True)
    self.assertTrue(subtable.isEquivalent(self.subtable))
    column = self.table.childFromName(COLUMN5, is_relative=True)
    self.assertTrue(column.isEquivalent(self.column5))

  def testColumnFromName(self):
    if IGNORE_TEST:
      return
    full_name = self.table._createFullName(self.subtable_column)
    column = self.table.columnFromName(full_name, is_relative=False)
    self.assertTrue(column.isEquivalent(self.subtable_column))
    column = self.table.columnFromName(COLUMN5, is_relative=True)
    self.assertTrue(column.isEquivalent(self.column5))
    self.assertIsNone(self.table.columnFromName(SUBTABLE, is_relative=True))

  def testGetCell(self):
    if IGNORE_TEST:
      return
    self.assertEqual(self.table.getCell(0, 1),
                     COLUMN1_CELLS[0])
    index = self.table.numColumns()
    with self.assertRaises(ValueError):
      self.table.getCell(0, index)
     

  def testInsertColumn(self):
    if IGNORE_TEST:
      return
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
    if IGNORE_TEST:
      return
    # Move column 2 to be after column 0
    dest_idx = 0
    column2 = self.table.columnFromName(COLUMN2)
    self.table.moveColumn(column2, dest_idx)
    self.assertEqual(self.table.getColumns()[dest_idx+1].getName(), COLUMN2)

  def testMoveChild(self):
    if IGNORE_TEST:
      return
    dest_idx = 0
    self.table.moveChild(self.subtable, dest_idx)
    self.assertEqual(self.table.getChildren()[dest_idx+1].getName(), 
        self.subtable.getName())

  def testNumColumns(self):
    if IGNORE_TEST:
      return
    self.assertEqual(self.table.numColumns(), 5)

  def testRemoveColumn(self):
    if IGNORE_TEST:
      return
    num_col = self.table.numColumns()
    column = self.table.getColumns()[1]
    self.table.removeColumn(column)
    self.assertEqual(self.table.numColumns(), num_col - 1)

  def testGetName(self):
    if IGNORE_TEST:
      return
    self.assertIsNone(self.table.setName("newTable"))
    self.assertIsNotNone(self.table.setName("new Table"))

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
    columns = self.table.getColumns()
    self.assertTrue(not self.subtable in columns)

if __name__ == '__main__':
  unittest.main()

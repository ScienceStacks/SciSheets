'''Tests for table'''

#from django.test import TestCase 
#mockfrom jviz.mvc_sheets import column as cl
import table as tb 
import column as cl
import errors as er
import numpy as np
from util_test import createColumn, createTable
import unittest


# Constants
COLUMN = "DUMMY COLUMN"
COLUMN1 = "DUMMY1 COLUMN"
COLUMN2 = "DUMMY2 COLUMN"
COLUMN3 = "DUMMY3 COLUMN"
COLUMN4 = "DUMMY4 COLUMN"
TABLE_NAME = "DUMMY TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
FORMULA = "A+B"
COLUMN1_CELLS = ["one", "two", "three"]
COLUMN2_CELLS = [10.0, 20.0, 30.0]


#############################
# Tests
#############################
class TestTable(unittest.TestCase):

  def setUp(self):
    self.table = createTable(TABLE_NAME)
    column1 = cl.Column(COLUMN1)
    column1.addCells(COLUMN1_CELLS)
    self.table.addColumn(column1)
    column2 = cl.Column(COLUMN2)
    column2.addCells(COLUMN2_CELLS)
    self.table.addColumn(column2)
    self.columns = self.table.getColumns()

  def testConstructor(self):
    table = tb.Table(TABLE_NAME)
    self.assertEqual(table._name, TABLE_NAME)
    self.assertEqual(len(table._columns), 1)
    self.assertEqual(table._columns[0].getName(), "row")

  def testAdjustColumnLength(self):
    table = createTable(TABLE_NAME)
    column = cl.Column(COLUMN)
    column.addCells(COLUMN1_CELLS)
    table.addColumn(column)
    column = cl.Column(COLUMN1)
    table._adjustColumnLength(column)
    self.assertEqual(column.numCells(), len(COLUMN1_CELLS))

  def testUpdateNameColumn(self):
    self.assertEqual(self.table._columns[0].numCells(),
                     self.table._columns[1].numCells())

  def testaddColumn(self):
    table = createTable(TABLE_NAME)
    # Add an empty column
    column = cl.Column(COLUMN)
    column.addCells(COLUMN1_CELLS)
    table.addColumn(column)
    # Add a column with the same name
    self.assertEqual(table._columns[1], column)
    with self.assertRaises(er.DuplicateColumnName):
      table.addColumn(column)
    table = createTable(TABLE_NAME)
    # Add a column with data
    column = cl.Column(COLUMN1)
    column.addCells(LIST)
    table.addColumn(column)
    self.assertEqual(column.numCells(), table.numRows())
    # Add a column that has more rows than the table
    column = cl.Column(COLUMN4)
    column.addCells(LIST)
    column.addCells(LIST)
    with self.assertRaises(er.InvalidColumnStructureForAddToTable):
      table.addColumn(column)

  def testGetRow(self):
    row = self.table.getRow()
    isCorrect = row.has_key(COLUMN1) and row.has_key(COLUMN2)
    self.assertTrue(isCorrect)
    isCorrect = row[COLUMN1] is None
    isCorrect = isCorrect and row[COLUMN2] is None
    IDX = 1
    row = self.table.getRow(IDX)
    isCorrect = row[COLUMN1] == COLUMN1_CELLS[IDX]
    isCorrect = isCorrect and row[COLUMN2] == COLUMN2_CELLS[IDX]
    self.assertTrue(isCorrect)

  def testAddRow(self):
    row = self.table.getRow()
    row[COLUMN1] = "four"
    row[COLUMN2] = 40.0
    self.table.addRow(row)
    expected_rows = len(COLUMN1_CELLS) + 1
    self.assertEqual(self.table.numRows(), expected_rows)
    column = self.columns[1]
    cells = column.getCells()
    self.assertEqual(cells[3], row[COLUMN1])

  def testCopy(self):
    new_table = self.table.copy()
    self.assertEqual(self.table.numRows(), new_table.numRows())
    self.assertEqual(self.table.numColumns(), new_table.numColumns())

  def testDeleteColumn(self):
    num_col = self.table.numColumns()
    column = self.table.columnFromName(COLUMN2)
    self.table.deleteColumn(column)
    self.assertEqual(num_col-1, self.table.numColumns())

  def testDeleteRows(self):
    ROWS = [0, 2]
    expected_rows = self.table.numRows() - len(ROWS)
    self.table.deleteRows(ROWS)
    self.assertEqual(self.table.numRows(), expected_rows)

  def testGetColumns(self):
    columns = self.table.getColumns()
    self.assertEqual(len(columns), self.table.numColumns())
    for c in columns:
      self.assertTrue(isinstance(c, cl.Column))

  def testNumColumns(self):
    self.assertEqual(self.table.numColumns(), 3)

  def testNumRows(self):
    self.assertEqual(self.table.numRows(), len(COLUMN2_CELLS))

  def testUpdateRow(self):
    rowidx = 1
    row = tb.Row()
    row[COLUMN1] = '10'
    row[COLUMN2] = 20.0
    self.table.updateRow(row, rowidx)
    row['row'] = self.table._rowNameFromIndex(rowidx)
    self.assertEqual(row, self.table.getRow(index=rowidx))

  def testMoveColumn(self):
    column2 = self.table.columnFromName(COLUMN2)
    self.table.moveColumn(column2, 1)
    self.assertEqual(self.table._columns[1].getName(), COLUMN2)
      

if __name__ == '__main__':
    unittest.man()

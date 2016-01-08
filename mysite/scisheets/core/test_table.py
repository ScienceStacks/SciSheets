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

  def testColumnFromIndex(self):
    COLUMN2_INDEX = 1
    column2 = self.table.columnFromIndex(COLUMN2_INDEX)
    self.assertEqual(column2.getName(), COLUMN1)

  def testInsertColumn(self):
    NEW_COLUMN_NAME = "NEW_COLUMN"
    index = 1
    new_column = cl.Column(NEW_COLUMN_NAME)
    self.table.insertColumn(new_column, index)
    self.assertEqual(self.table._columns[index].getName(), 
        NEW_COLUMN_NAME)
    NEWER_COLUMN_NAME = "NEWER_COLUMN"
    newer_column = cl.Column(NEWER_COLUMN_NAME)
    index = len(self.table._columns)
    self.table.insertColumn(newer_column)
    self.assertEqual(self.table._columns[index].getName(), 
        NEWER_COLUMN_NAME)

  def testRemoveColumn(self):
    num_col = self.table.numColumns()
    column = self.table.getColumns()[1]
    self.table.removeColumn(column)
    self.assertEqual(self.table.numColumns(), num_col - 1)

  def testInsertRow(self):
    row = self.table.getRow()  # Get an empty row
    row[COLUMN1] = "four"
    row[COLUMN2] = 50
    index = 0
    self.table.insertRow(row, index=index)
    columns = self.table.getColumns()
    self.assertEqual(columns[1].getCells()[index], "four")
    self.assertEqual(columns[2].getCells()[index], 50)
    index = len(columns[1].getCells())
    self.table.insertRow(row)
    self.assertEqual(columns[1].getCells()[index], "four")
    self.assertEqual(columns[2].getCells()[index], 50)

  def testMoveRow(self):
    cur_row = self.table.getRow(1)
    self.table.moveRow(1,2)
    new_row = self.table.getRow(2)
    for k in cur_row.keys():
      if k != 'row':
        self.assertEqual(cur_row[k], new_row[k])

  def testUpdateCell(self):
    NEW_VALUE = "onee"
    COLUMN_INDEX = 1
    ROW_INDEX = 0
    self.table.updateCell("onee", ROW_INDEX, COLUMN_INDEX)
    columns = self.table.getColumns()
    self.assertEqual(columns[COLUMN_INDEX].getCells()[ROW_INDEX],
        NEW_VALUE)

  def testUpdateRow(self):
    row = self.table.getRow()  # Get an empty row
    row[COLUMN1] = "four"
    row[COLUMN2] = 50
    INDEX = 0
    self.table.updateRow(row, index=INDEX)
    new_row = self.table.getRow(INDEX)
    self.assertEqual(new_row[COLUMN1], row[COLUMN1])
    self.assertEqual(new_row[COLUMN2], row[COLUMN2])

  def testGetCell(self):
    self.assertEqual(self.table.getCell(0, 1),
                     COLUMN1_CELLS[0])

  def testRowNamesFromSize(self):
    SIZE = 5
    table = self.table
    row_names = table._rowNamesFromSize(SIZE)
    self.assertEqual(len(row_names), SIZE)
    for n in range(SIZE):
      self.assertEqual(row_names[n], table._rowNameFromIndex(n))

  def testRenameRow(self):
    table = self.table
    ROW_IDX = 0
    columns = table.getColumns()
    table_data = []
    # Save current table data
    for c in columns:
      table_data.append(c.getCells())
    # Move the first row to the end of the table
    after_last_row_name = table._rowNameFromIndex(table.numRows())
    table.renameRow(ROW_IDX, after_last_row_name)
    # Test if done correctly
    rplIdx = range(len(COLUMN1_CELLS))
    del rplIdx[0]
    rplIdx.append(0)
    for c in range(1, table.numColumns()):
      new_array = table_data[c][rplIdx]
      for r in range(table.numRows()):
        self.assertEqual(table.getCell(r, c), new_array[r])

if __name__ == '__main__':
    unittest.main()

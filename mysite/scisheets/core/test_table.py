'''Tests for table'''

import table as tb
import column as cl
import errors as er
from util_test import createTable
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
COLUMN2_CELLS = [10.0, 20.0, 30.0]
COLUMN5_CELLS = [100.0, 200.0, 300.0]


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestTable(unittest.TestCase):

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
    column.addCells(['aa'])
    table._adjustColumnLength(column)
    self.assertEqual(column.numCells(), len(COLUMN1_CELLS))
    self.assertIsNone(column.getCells()[1])
    column = cl.Column("YetAnotherColumn")
    column.addCells([1])
    table._adjustColumnLength(column)
    self.assertEqual(column.numCells(), len(COLUMN1_CELLS))
    self.assertTrue(np.isnan(column.getCells()[1]))

  def testUpdateNameColumn(self):
    self.assertEqual(self.table._columns[0].numCells(),
                     self.table._columns[1].numCells())

  def testAddColumn(self):
    table = createTable(TABLE_NAME)
    # Add an empty column
    column = cl.Column(COLUMN)
    column.addCells(COLUMN1_CELLS)
    table.addColumn(column)
    # Add a column with the same name
    self.assertEqual(table._columns[1], column)
    error = table.addColumn(column)
    self.assertIsNotNone(error)
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
    with self.assertRaises(er.InternalError):
      table.addColumn(column)

  def testGetRow(self):
    row = self.table.getRow()
    is_correct = row.has_key(COLUMN1) and row.has_key(COLUMN2)
    self.assertTrue(is_correct)
    is_correct = row[COLUMN1] is None
    is_correct = is_correct and row[COLUMN2] is None
    idx = 1
    row = self.table.getRow(idx)
    is_correct = row[COLUMN1] == COLUMN1_CELLS[idx]
    is_correct = is_correct and row[COLUMN2] == COLUMN2_CELLS[idx]
    self.assertTrue(is_correct)

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
    #
    self.table.addRow(row, -0.1)  # Make it the first row
    expected_rows += 1
    self.assertEqual(self.table.numRows(), expected_rows)
    column = self.columns[1]
    cells = column.getCells()
    self.assertEqual(cells[0], row[COLUMN1])

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
    rows = [0, 2]
    expected_rows = self.table.numRows() - len(rows)
    self.table.deleteRows(rows)
    self.assertEqual(self.table.numRows(), expected_rows)

  def testGetColumns(self):
    columns = self.table.getColumns()
    self.assertEqual(len(columns), self.table.numColumns())
    for column in columns:
      self.assertTrue(isinstance(column, cl.Column))

  def testNumColumns(self):
    self.assertEqual(self.table.numColumns(), 4)

  def testNumRows(self):
    self.assertEqual(self.table.numRows(), len(COLUMN2_CELLS))

  def testMoveColumn1(self):
    # Move column 2 to be after column 0
    dest_idx = 0
    column2 = self.table.columnFromName(COLUMN2)
    self.table.moveColumn(column2, dest_idx)
    self.assertEqual(self.table._columns[dest_idx+1].getName(), COLUMN2)

  def testMoveColumn2(self):
    # Move column 1 to be after column 3
    dest_idx = 3
    column1 = self.table.columnFromName(COLUMN1)
    self.table.moveColumn(column1, dest_idx)
    self.assertEqual(self.table._columns[dest_idx].getName(), COLUMN1)

  def testColumnFromIndex(self):
    columns = self.table.getColumns()
    for idx in range(self.table.numColumns()):
      column = columns[idx]
      self.assertEqual(idx, self.table.indexFromColumn(column))

  def testInsertColumn(self):
    new_column_name = "NEW_COLUMN"
    index = 1
    new_column = cl.Column(new_column_name)
    self.table.insertColumn(new_column, index)
    self.assertEqual(self.table._columns[index].getName(),
        new_column_name)
    newer_column_name = "NEWER_COLUMN"
    newer_column = cl.Column(newer_column_name)
    index = len(self.table._columns)
    self.table.insertColumn(newer_column)
    self.assertEqual(self.table._columns[index].getName(),
        newer_column_name)

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
    self.table.moveRow(1, 2)
    new_row = self.table.getRow(2)
    for k in cur_row.keys():
      if k != 'row':
        self.assertEqual(cur_row[k], new_row[k])

  def testUpdateCell(self):
    new_value = "onee"
    row_index = 0
    self.table.updateCell("onee", row_index, COLUMN2_INDEX)
    columns = self.table.getColumns()
    self.assertEqual(columns[COLUMN2_INDEX].getCells()[row_index],
        new_value)

  def testUpdateRow(self):
    # Simple update
    rowidx = 1
    row = tb.Row()
    row[COLUMN1] = '10'
    row[COLUMN2] = 20.0
    row[COLUMN5] = 200.0
    self.table.updateRow(row, rowidx)
    row['row'] = tb.Table._rowNameFromIndex(rowidx)
    self.assertEqual(row, self.table.getRow(index=rowidx))
    # More complex update
    row = self.table.getRow()  # Get an empty row
    row[COLUMN1] = "four"
    row[COLUMN2] = 50
    idx = 0
    self.table.updateRow(row, index=idx)
    new_row = self.table.getRow(idx)
    self.assertEqual(new_row[COLUMN1], row[COLUMN1])
    self.assertEqual(new_row[COLUMN2], row[COLUMN2])

  def testGetCell(self):
    self.assertEqual(self.table.getCell(0, 1),
                     COLUMN1_CELLS[0])

  def testRowNamesFromSize(self):
    size = 5
    row_names = tb.Table._rowNamesFromSize(size)
    self.assertEqual(len(row_names), size)
    for idx in range(size):
      self.assertEqual(row_names[idx], tb.Table._rowNameFromIndex(idx))

  def testRenameRow(self):
    table = self.table
    row_idx = 0
    columns = table.getColumns()
    table_data = table.getData()
    # Move the first row to the end of the table
    after_last_row_name = tb.Table._rowNameFromIndex(table.numRows())
    table.renameRow(row_idx, after_last_row_name)
    # Test if done correctly
    rpl_idx = range(len(COLUMN1_CELLS))
    del rpl_idx[0]
    rpl_idx.append(0)
    for idx in range(1, table.numColumns()):
      expected_array = table_data[idx][rpl_idx]
      is_equal = (columns[idx].getCells() == expected_array).all()
      self.assertTrue(is_equal)

  def testRenameColumn(self):
    column = self.table.columnFromName(COLUMN1)
    is_equal = self.table.renameColumn(column, COLUMN1)
    self.assertFalse(is_equal)
    new_name = "%s_extra" % COLUMN1
    is_equal = self.table.renameColumn(column, new_name)
    self.assertTrue(is_equal)

  def testTrimRows(self):
    num_rows = self.table.numRows()
    self.table.trimRows()
    self.assertEqual(num_rows, self.table.numRows())
    row = self.table.getRow()
    self.table.addRow(row)
    self.table.trimRows()
    self.assertEqual(num_rows, self.table.numRows())
    self.table.addRow(row, ext_index=0)
    self.table.trimRows()
    self.assertEqual(num_rows+1, self.table.numRows())


if __name__ == '__main__':
  unittest.main()

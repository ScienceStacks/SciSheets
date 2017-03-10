""" Tests for table """

from mysite import settings
from scisheets.core.helpers.serialize_deserialize import CLASS_VARIABLE
import scisheets.core.helpers.cell_types as cell_types
import scisheets.core.table as tb
import scisheets.core.column as cl
import scisheets.core.errors as er
import scisheets.core.helpers_test as ht
import numpy as np
import os
import pandas as pd
import unittest


TEST_TABLE_1 = os.path.join(settings.SCISHEETS_TEST_DIR,
    "test_table_1")

IGNORE_TEST = False


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestTable(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)

  def testConstructor(self):
    if IGNORE_TEST:
      return
    table = tb.Table(ht.TABLE_NAME)
    self.assertEqual(table._name, ht.TABLE_NAME)
    self.assertEqual(len(table.getColumns()), 1)
    self.assertEqual(table.getColumns()[0].getName(), "row")
    self.assertTrue('import' in table._prologue.getFormula())

  def testAdjustColumnLength(self):
    if IGNORE_TEST:
      return
    table = ht.createTable(ht.TABLE_NAME)
    column = cl.Column(ht.COLUMN)
    column.addCells(ht.COLUMN1_CELLS)
    table.addColumn(column)
    column = cl.Column(ht.COLUMN1)
    column.addCells(['aa'])
    table.addColumn(column)
    table.adjustColumnLength()
    self.assertEqual(column.numCells(), table.numRows())
    self.assertIsNone(column.getCells()[1])
    column = cl.Column("YetAnotherColumn")
    column.addCells([1])
    table.addColumn(column)
    table.adjustColumnLength()
    self.assertEqual(column.numCells(), table.numRows())
    if column.isFloats():
      self.assertTrue(np.isnan(column.getCells()[1]))  # pylint: disable=E1101
    else:
      self.assertIsNone(column.getCells()[1])

  def testUpdateNameColumn(self):
    if IGNORE_TEST:
      return
    self.assertEqual(self.table.getColumns()[0].numCells(),
                     self.table.getColumns()[1].numCells())

  def testAddColumn(self):
    if IGNORE_TEST:
      return
    table = ht.createTable(ht.TABLE_NAME)
    # Add an empty column
    column = cl.Column(ht.COLUMN)
    column.addCells(ht.COLUMN1_CELLS)
    table.addColumn(column)
    # Add a column with the same name
    self.assertEqual(table.getColumns()[1], column)
    error = table.addColumn(column)
    self.assertIsNotNone(error)
    table = ht.createTable(ht.TABLE_NAME)
    # Add a column with data
    column = cl.Column(ht.COLUMN1)
    column.addCells(ht.LIST)
    table.addColumn(column)
    self.assertEqual(column.numCells(), table.numRows())

  def testGetRow(self):
    if IGNORE_TEST:
      return
    row = self.table.getRow()
    is_correct = row.has_key(ht.COLUMN1) and row.has_key(ht.COLUMN2)
    self.assertTrue(is_correct)
    is_correct = row[ht.COLUMN1] is None
    is_correct = is_correct and row[ht.COLUMN2] is None
    idx = 1
    row = self.table.getRow(row_index=idx)
    is_correct = row[ht.COLUMN1] == ht.COLUMN1_CELLS[idx]
    is_correct = is_correct and row[ht.COLUMN2] == ht.COLUMN2_CELLS[idx]
    self.assertTrue(is_correct)

  def testAddRow1(self):
    if IGNORE_TEST:
      return
    column = self.table.columnFromName(ht.COLUMN2)
    self.assertEqual(np.array(column.getCells()).dtype,
        np.float64)  # pylint: disable=E1101
    row = self.table.getRow()
    self.table.addRow(row)
    expected_rows = len(ht.COLUMN1_CELLS) + 1
    self.assertEqual(self.table.numRows(), expected_rows)
    self.assertEqual(np.array(column.getCells()).dtype,
        np.float64) # pylint: disable=E1101
    #
    expected_rows = len(ht.COLUMN1_CELLS) + 2
    row = self.table.getRow()
    self.table.addRow(row, row_index=0)
    self.assertEqual(self.table.numRows(), expected_rows)

  def testAddRow2(self):
    if IGNORE_TEST:
     return
    expected_rows = self.table.numRows() + 1
    row = self.table.getRow()
    row[ht.COLUMN1] = "four"
    row[ht.COLUMN2] = 40.0
    self.table.addRow(row)
    self.assertEqual(self.table.numRows(), expected_rows)
    column = self.table.getColumns()[1]
    cells = column.getCells()
    self.assertEqual(cells[3], row[ht.COLUMN1])
    #
    row = self.table.getRow()
    row[ht.COLUMN1] = "four"
    row[ht.COLUMN2] = 40.0
    self.table.addRow(row, -0.1)  # Make it the first row
    expected_rows += 1
    self.assertEqual(self.table.numRows(), expected_rows)
    column = self.table.getColumns()[1]
    cells = column.getCells()
    self.assertEqual(cells[0], row[ht.COLUMN1])

  def testCopy(self):
    if IGNORE_TEST:
     return
    new_table = self.table.copy()
    self.assertEqual(self.table.numRows(), new_table.numRows())
    self.assertEqual(self.table.numColumns(), new_table.numColumns())
    self.assertTrue(new_table.isEquivalent(self.table))
    

  def testDeleteColumn(self):
    if IGNORE_TEST:
      return
    num_col = self.table.numColumns()
    column = self.table.columnFromName(ht.COLUMN2)
    self.table.deleteColumn(column)
    self.assertEqual(num_col-1, self.table.numColumns())

  def testDeleteRows(self):
    if IGNORE_TEST:
      return
    rows = [0, 2]
    expected_rows = self.table.numRows() - len(rows)
    self.table.deleteRows(rows)
    self.assertEqual(self.table.numRows(), expected_rows)

  def testGetColumns(self):
    if IGNORE_TEST:
      return
    columns = self.table.getColumns()
    self.assertEqual(len(columns), self.table.numColumns())
    for column in columns:
      self.assertTrue(isinstance(column, cl.Column))

  def testNumColumns(self):
    if IGNORE_TEST:
      return
    self.assertEqual(self.table.numColumns(), self.num_columns)

  def testNumRows(self):
    if IGNORE_TEST:
      return
    self.assertEqual(self.table.numRows(), len(ht.COLUMN2_CELLS))

  def testInsertRow(self):
    if IGNORE_TEST:
      return
    row = self.table.getRow()  # Get an empty row
    row[ht.COLUMN1] = "four"
    row[ht.COLUMN2] = 50
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
    if IGNORE_TEST:
      return
    cur_row = self.table.getRow(row_index=1)
    self.table.moveRow(1, 2)
    new_row = self.table.getRow(row_index=2)
    for k in cur_row.keys():
      column = self.table.columnFromName(k)
      if not tb.Table.isNameColumn(column):
        if k != 'row':
          if cur_row[k] != new_row[k]:
            import pdb; pdb.set_trace()
          self.assertEqual(cur_row[k], new_row[k])

  def testUpdateCell(self):
    if IGNORE_TEST:
      return
    new_value = "onee"
    row_index = 0
    self.table.updateCell("onee", row_index, ht.COLUMN2_INDEX)
    columns = self.table.getColumns()
    self.assertEqual(columns[ht.COLUMN2_INDEX].getCells()[row_index],
        new_value)

  def testUpdateRow(self):
    if IGNORE_TEST:
      return
    # Simple update
    rowidx = 1
    row = tb.Row()
    row[ht.COLUMN1] = '10'
    row[ht.COLUMN2] = 20.0
    row[ht.COLUMN5] = 200.0
    self.table.updateRow(row, rowidx)
    row['row'] = tb.Table._rowNameFromIndex(rowidx)
    this_row = self.table.getRow(row_index=rowidx)
    for name in row:
      self.assertEqual(row[name], this_row[name])
    # More complex update
    row = self.table.getRow()  # Get an empty row
    row[ht.COLUMN1] = "four"
    row[ht.COLUMN2] = 50
    idx = 0
    self.table.updateRow(row, index=idx)
    new_row = self.table.getRow(row_index=idx)
    self.assertEqual(new_row[ht.COLUMN1], row[ht.COLUMN1])
    self.assertEqual(new_row[ht.COLUMN2], row[ht.COLUMN2])

  def testRowNamesFromSize(self):
    if IGNORE_TEST:
      return
    size = 5
    row_names = tb.Table._rowNamesFromSize(size)
    self.assertEqual(len(row_names), size)
    for idx in range(size):
      self.assertEqual(row_names[idx], tb.Table._rowNameFromIndex(idx))

  def testRenameRow(self):
    if IGNORE_TEST:
      return
    table = self.table
    row_idx = 0
    columns = table.getColumns()
    old_table_data = table.getData()
    # Move the first row to the end of the table
    after_last_row_name = tb.Table._rowNameFromIndex(table.numRows())
    table.renameRow(row_idx, after_last_row_name)
    new_table_data = table.getData()
    # Test if done correctly
    rpl_idx = range(len(ht.COLUMN1_CELLS))
    del rpl_idx[0]
    rpl_idx.append(0)
    for column in self.table.getColumns():
      if not tb.Table.isNameColumn(column):
        expected_array = [old_table_data[column.getName()][n] 
            for n in rpl_idx]
        self.assertEqual(expected_array, column.getCells())
    for name in old_table_data:
      expected_array = [old_table_data[name][n] for n in rpl_idx]
      column = self.table.columnFromName(name)
      if not tb.Table.isNameColumn(column):
        is_equal = expected_array == column.getCells()
        if not is_equal:
          import pdb; pdb.set_trace()
        self.assertTrue(is_equal)

  def testRenameColumn(self):
    if IGNORE_TEST:
      return
    column = self.table.columnFromName(ht.COLUMN1)
    is_equal = self.table.renameColumn(column, ht.COLUMN1)
    self.assertFalse(is_equal)
    new_name = "%s_extra" % ht.COLUMN1
    is_equal = self.table.renameColumn(column, new_name)
    self.assertTrue(is_equal)

  def testTrimRows(self):
    if IGNORE_TEST:
      return
    num_rows = self.table.numRows()
    self.table.trimRows()
    self.assertEqual(num_rows, self.table.numRows())
    row = self.table.getRow()
    self.table.addRow(row)
    self.table.trimRows()
    self.assertEqual(num_rows, self.table.numRows())
    self.table.addRow(row, row_index=0)
    self.table.trimRows()
    self.assertEqual(num_rows+1, self.table.numRows())

  def testRefactorColumn(self):
    if IGNORE_TEST:
      return
    table = ht.createTable("test", 
        column_name=[ht.COLUMN1, ht.COLUMN2, ht.COLUMN3])
    column1 = table.columnFromName(ht.COLUMN1)
    formula1 = "range(5)"
    column1.setFormula(formula1)
    column2 = table.columnFromName(ht.COLUMN2)
    formula2 = "%s = [5*x for x in %s]" % (ht.COLUMN2, ht.COLUMN1)
    column2.setFormula(formula2)
    table.evaluate(user_directory=ht.TEST_DIR)
    expected_values = [5*x for x in range(5)]
    actual_values = [x for x in column2.getCells()]
    self.assertTrue(expected_values == actual_values)
    new_name = "%s_new" % ht.COLUMN1
    table.refactorColumn(ht.COLUMN1, new_name)
    table.evaluate(user_directory=ht.TEST_DIR)
    column = table.columnFromName(new_name)
    self.assertIsNotNone(column)
    expected_values = range(5)
    actual_values = [x for x in column.getCells()]
    self.assertTrue(expected_values == actual_values)

  def testIsEquivalent(self):
    if IGNORE_TEST:
     return
    new_table = self.table.copy()
    self.assertTrue(self.table.isEquivalent(new_table))
    column = new_table.columnFromIndex(1)
    this_column = self.table.columnFromName(column.getName())
    column = new_table.columnFromIndex(1)
    cell = column.getCell(0)
    new_cell = "New%s" % str(cell)
    column.updateCell(new_cell, 0)
    self.assertFalse(self.table.isEquivalent(new_table))
    this_column.updateCell(new_cell, 0)
    self.assertTrue(self.table.isEquivalent(new_table))
    self.table.deleteColumn(this_column)
    self.assertFalse(self.table.isEquivalent(new_table))

  def testIsEquivalent(self):
    if IGNORE_TEST:
     return
    [table, other] = ht.getCapture("test_table_2")
    #self.assertTrue(table.isEquivalent(other))

  def testGetColumnFormula(self):
    if IGNORE_TEST:
      return
    table = ht.createTable("test", column_name=[ht.COLUMN1, ht.COLUMN2])
    column1 = table.columnFromName(ht.COLUMN1)
    self.assertEqual(len(table.getFormulaColumns()), 0)
    formula1 = "range(5)"
    column1.setFormula(formula1)
    self.assertEqual(len(table.getFormulaColumns()), 1)
    column2 = table.columnFromName(ht.COLUMN2)
    formula2 = "[2*x for x in %s]" % ht.COLUMN1
    column2.setFormula(formula2)
    self.assertEqual(len(table.getFormulaColumns()), 2)
    column2.setFormula(None)
    self.assertEqual(len(table.getFormulaColumns()), 1)

  def testGetSerializationDict(self):
    if IGNORE_TEST:
      return
    serialization_dict = self.table.getSerializationDict(CLASS_VARIABLE)
    self.assertTrue(CLASS_VARIABLE in serialization_dict.keys())
    children = serialization_dict['_children']
    is_presents = [CLASS_VARIABLE in c.keys() for c in children]
    self.assertTrue(all(is_presents))
    excludes = ['_prologue_formula', 
                '_epilogue_formula', 
                '_filepath', 
                CLASS_VARIABLE,
               ]
    for key in serialization_dict.keys():
      if not key in excludes:
        self.assertTrue(key in self.table.__dict__.keys(), "%s"% key)

  # TODO: Add test where there is a child that is a Table
  def testDeserialize(self):
    if IGNORE_TEST:
      return
    serialization_dict = self.table.getSerializationDict(CLASS_VARIABLE)
    table = tb.Table.deserialize(serialization_dict)
    self.assertTrue(table.isEquivalent(self.table))

  def testGetDataColumns(self):
    if IGNORE_TEST:
      return
    columns = self.table.getDataColumns()
    num = 0
    for column in self.table.getColumns():
      if not tb.Table.isNameColumn(column):
        num += 1
    self.assertEqual(len(columns), num)
      

if __name__ == '__main__':
  unittest.main()

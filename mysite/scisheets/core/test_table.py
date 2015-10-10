'''Tests for table'''

#from django.test import TestCase 
#mockfrom jviz.mvc_sheets import column as cl
import table as tb 
import column as cl
import unittest
import errors as er
import numpy as np
from util_test import CreateColumn, CompareValues, ToList, CreateTable


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
    self.table = CreateTable(TABLE_NAME)
    self.columns = self.table.GetColumns()
    column = cl.Column(COLUMN1)
    self.table.AddColumn(column)
    self.columns.append(column)
    column.AddCells(COLUMN1_CELLS)
    column = cl.Column(COLUMN2)
    column.AddCells(COLUMN2_CELLS)
    self.table.AddColumn(column)
    self.columns.append(column)

  def testConstructor(self):
    table = tb.Table(TABLE_NAME)
    self.assertEqual(table._name, TABLE_NAME)
    self.assertIsNone(table._name_column)
    self.assertEqual(len(table._columns), 1)

  def testAddColumn(self):
    table = CreateTable(TABLE_NAME)
    # Add an empty column
    column = cl.Column(COLUMN)
    table.AddColumn(column)
    # Add a column with the same name
    self.assertEqual(table._columns[COLUMN], column)
    with self.assertRaises(er.DuplicateColumnName):
      table.AddColumn(column)
    table = CreateTable(TABLE_NAME)
    # Add a column with data
    column = cl.Column(COLUMN)
    column.AddCells(LIST)
    table.AddColumn(column)
    self.assertEqual(len(table._columns[COLUMN].GetCells()), 
        len(LIST))
    column = cl.Column(COLUMN2)
    column.AddCells(LIST2)
    table.AddColumn(column)
    self.assertEqual(len(table._columns[COLUMN2].GetCells()), 
        len(LIST))
    # Add a column that has more rows than the table
    column = cl.Column(COLUMN4)
    column.AddCells(LIST)
    column.AddCells(LIST)
    table.AddColumn(column)
    # Verify that cells were added
    self.assertEqual(len(table._columns[COLUMN4].GetCells()), 
        2*len(LIST))

  def testAddRow(self):
    ROW = ["four", 40.0]
    self.table.AddRow(ROW)
    self.assertEqual(self.table.GetNumRows(), 4)
    column = self.columns[0]
    cells = column.GetCells()
    self.assertEqual(cells[3], ROW[0])

  def testCopy(self):
    new_table = self.table.Copy()
    self.assertEqual(self.table.GetNumRows(), new_table.GetNumRows())
    self.assertEqual(self.table.GetNumColumns(), new_table.GetNumColumns())

  def testDeleteColumn(self):
    num_col = self.table.GetNumColumns()
    self.table.DeleteColumn(COLUMN2)
    self.assertEqual(num_col-1, self.table.GetNumColumns())

  def testDeleteRows(self):
    ROWS = [0, 2]
    self.table.DeleteRows(ROWS)
    #TODO: Adjust test when have 'None' cleanup logics
    #self.assertEqual(self.table.GetNumRows(), len(COLUMN1_CELLS)-len(ROWS))

  def testGetColumns(self):
    columns = self.table.GetColumns()
    self.assertEqual(len(columns), self.table.GetNumColumns())
    for c in columns:
      self.assertTrue(isinstance(c, cl.Column))

  def testGetColumnObject(self):
    column = self.table.GetColumnObject(COLUMN1)
    self.assertEqual(column.GetName(), COLUMN1)
    column1 = self.table.GetColumnObject(1)
    self.assertEqual(column, column1)
    column1 = self.table.GetColumnObject(column)
    self.assertEqual(column, column1)

  def testGetColumnPosition(self):
    n = -1
    for c in self.columns:
      n += 1
      pos = self.table.GetColumnPosition(c.GetName())
      self.assertEqual(pos, n)

  def testGetNumColumns(self):
    self.assertEqual(self.table.GetNumColumns(), 3)

  def testGetNumRows(self):
    self.assertEqual(self.table.GetNumRows(), len(COLUMN2_CELLS))

  def testUpdateRow(self):
    rowidx = 1
    NEW_ROW0 = [COLUMN1_CELLS[rowidx], COLUMN2_CELLS[rowidx]]
    self.table.UpdateRow(0, NEW_ROW0)
    rowdict = self.table.GetRows()
    rowl = [rowdict[COLUMN1][rowidx], rowdict[COLUMN2][rowidx]]
    for n in range(len(NEW_ROW0)):
      self.assertEqual(NEW_ROW0[n], rowl[n])
      

if __name__ == '__main__':
    unittest.main()

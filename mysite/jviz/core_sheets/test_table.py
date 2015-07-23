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
COLUMN_NAME = "DUMMY COLUMN"
COLUMN_NAME2 = "DUMMY2 COLUMN"
COLUMN_NAME3 = "DUMMY3 COLUMN"
COLUMN_NAME4 = "DUMMY4 COLUMN"
TABLE_NAME = "DUMMY TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
FORMULA = "A+B"


#############################
# Tests
#############################
class TestTable(unittest.TestCase):

  def testConstructor(self):
    table = tb.Table(TABLE_NAME)
    self.assertEqual(table._name, TABLE_NAME)
    self.assertIsNone(table._name_column)
    self.assertEqual(len(table._columns), 0)

  def testAddColumn(self):
    table = CreateTable(TABLE_NAME)
    # Add an empty column
    column = cl.Column(COLUMN_NAME)
    table.AddColumn(column)
    # Add a column with the same name
    self.assertEqual(table._columns[COLUMN_NAME], column)
    with self.assertRaises(er.DuplicateColumnName):
      table.AddColumn(column)
    table = CreateTable(TABLE_NAME)
    # Add a column with data
    column = cl.Column(COLUMN_NAME)
    column.AddCells(LIST)
    table.AddColumn(column)
    self.assertEqual(len(table._columns[COLUMN_NAME].GetCells()), 
        len(LIST))
    column = cl.Column(COLUMN_NAME2)
    column.AddCells(LIST2)
    table.AddColumn(column)
    self.assertEqual(len(table._columns[COLUMN_NAME2].GetCells()), 
        len(LIST))
    # Add a column that has more rows than the table
    column = cl.Column(COLUMN_NAME4)
    column.AddCells(LIST)
    column.AddCells(LIST)
    table.AddColumn(column)
    # Verify that cells were added
    self.assertEqual(len(table._columns[COLUMN_NAME4].GetCells()), 
        2*len(LIST))

  def testAddRow(self):
    table = CreateTable(TABLE_NAME)
    


if __name__ == '__main__':
    unittest.main()

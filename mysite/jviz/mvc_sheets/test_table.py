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
TABLE_NAME = "DUMMY TABLE"
LIST = [2.0, 3.0]
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
    column = cl.Column(COLUMN_NAME)
    table.AddColumn(column)
    self.assertEqual(table._columns[COLUMN_NAME], column)
    with self.assertRaises(er.DuplicateColumnName):
      table.AddColumn(column)


if __name__ == '__main__':
    unittest.main()

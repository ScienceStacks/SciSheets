'''Tests for column'''

#from django.test import TestCase 
#mockfrom jviz.mvc_sheets import column as cl
import column as cl
import unittest
import errors as ex
import numpy as np
from util_test import CreateColumn, CompareValues, ToList

# Constants
COLUMN_NAME = "DUMMY"
LIST = [2.0, 3.0]
TABLE = 'DUMMY'
FORMULA = "A+B"


#############################
# Tests
#############################
class TestColumn(unittest.TestCase):

  def testConstructor(self):
    column = cl.Column(COLUMN_NAME)
    self.assertEqual(column._name, COLUMN_NAME)
    self.assertIsNone(column._owning_table)
    self.assertIsNone(column._formula)

  def testAddCells(self):
    SINGLE = 1.0
    LIST = [2.0, 3.0]
    ARRAY = np.array(LIST)
    column = cl.Column(COLUMN_NAME)
    column.AddCells(SINGLE)
    self.assertTrue(CompareValues(column._data_values, SINGLE))
    column = cl.Column(COLUMN_NAME)
    column.AddCells(LIST)
    self.assertTrue(CompareValues(column._data_values, LIST))
    column = cl.Column(COLUMN_NAME)
    column.AddCells(ARRAY)
    self.assertTrue(CompareValues(column._data_values, ARRAY))

  def testCopy(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    column_copy = column.Copy()
    self.assertEqual(column._name, column_copy._name)
    self.assertTrue(CompareValues(column._data_values, column_copy._data_values))
    self.assertEqual(column._formula, column_copy._formula)
    self.assertIsNone(column_copy._owning_table)

  def testDelCells(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    column.DelCells()
    self.assertEqual(len(column._data_values), 0)
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    INDEX = 0
    NON_INDEX = 1
    column.DelCells([INDEX])
    self.assertEqual(column._data_values[INDEX], LIST[NON_INDEX])

  def testEvaluate(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    self.assertRaises(ex.NotYetImplemented, column.Evaluate)

  def testGetCells(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    cells = column.GetCells()
    self.assertTrue(CompareValues(column._data_values, cells))

  def testGetNumCells(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    self.assertEqual(column.GetNumCells(), len(LIST))

  def testGetColumnName(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    self.assertEqual(column.GetColumnName(), column._name)

  def testSetFormula(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=None)
    column.SetFormula(FORMULA)
    self.assertEqual(column._formula, FORMULA)

  def testSetTable(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=None,
        formula=FORMULA)
    column.SetTable(TABLE)
    self.assertEqual(column._owning_table, TABLE)

  def testUpdateCell(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=None,
        formula=FORMULA)
    INDEX = 0
    new_value = LIST[INDEX] + 10
    column.UpdateCell(INDEX, new_value)
    self.assertEqual(column._data_values[INDEX], new_value)
    
    


if __name__ == '__main__':
    unittest.main()

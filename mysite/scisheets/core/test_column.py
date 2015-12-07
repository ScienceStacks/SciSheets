'''Tests for column'''

import column as cl
import unittest
import errors as er
import numpy as np
from util_test import createColumn, compareValues, toList

# Constants
COLUMN_NAME = "DUMMY"
COLUMN_STR_NAME = "DUMMY STR"
LIST = [2.0, 3.0]
LIST_STR = ["aa bb", "cc"]
TABLE = 'DUMMY'
FORMULA = "A+B"


#############################
# Tests
#############################
class TestColumn(unittest.TestCase):

  def setUp(self):
    self.column = createColumn(COLUMN_NAME, data=LIST, table=None,
        formula=FORMULA)
    self.column_str = createColumn(COLUMN_STR_NAME, data=LIST_STR, 
        table=None, formula=FORMULA)

  def testConstructor(self):
    column = cl.Column(COLUMN_NAME)
    self.assertEqual(column._name, COLUMN_NAME)
    self.assertIsNone(column._owning_table)
    self.assertIsNone(column._formula)

  def testAddCellsFloat(self):
    SINGLE_FLOAT = 1.0
    LIST_FLOAT = [2.0, 3.0]
    ARRAY = np.array(LIST_FLOAT)
    column = cl.Column(COLUMN_NAME)
    column.addCells(SINGLE_FLOAT)
    self.assertTrue(compareValues(column._data_values, SINGLE_FLOAT))
    self.assertEqual(column._data_type, float)
    column = cl.Column(COLUMN_NAME)
    column.addCells(LIST_FLOAT)
    self.assertTrue(compareValues(column._data_values, LIST_FLOAT))
    column = cl.Column(COLUMN_NAME)
    column.addCells(ARRAY)
    self.assertTrue(compareValues(column._data_values, ARRAY))

  def testAddCellsStr(self):
    SINGLE_STR = "cccc ccc"
    LIST_STR = ["aa", "bbb bb"]
    ARRAY = np.array(LIST_STR)
    column = cl.Column(COLUMN_NAME)
    column.addCells(SINGLE_STR)
    self.assertTrue(compareValues(column._data_values, SINGLE_STR))
    self.assertEqual(column._data_type, str)
    column = cl.Column(COLUMN_NAME)
    column.addCells(LIST_STR)
    self.assertTrue(compareValues(column._data_values, LIST_STR))
    column = cl.Column(COLUMN_NAME)
    column.addCells(ARRAY)
    self.assertTrue(compareValues(column._data_values, ARRAY))

  def testCopy(self):
    column_copy = self.column.copy()
    self.assertEqual(self.column._name, column_copy._name)
    self.assertEqual(self.column._data_type, column_copy._data_type)
    self.assertTrue(compareValues(self.column._data_values, 
        column_copy._data_values))
    self.assertEqual(self.column._formula, column_copy._formula)
    self.assertIsNone(column_copy._owning_table)

  def testDeleteCells(self):
    INDEX = 0
    NON_INDEX = 1
    self.column.deleteCells([INDEX])
    self.assertEqual(self.column._data_values[INDEX], LIST[NON_INDEX])

  def testEvaluate(self):
    self.assertRaises(er.NotYetImplemented, self.column.evaluate)

  def testDataType(self):
    self.assertEqual(self.column.getDataType(), float)
    self.assertEqual(self.column_str.getDataType(), str)

  def testGetCells(self):
    cells = self.column.getCells()
    self.assertTrue(compareValues(self.column._data_values, cells))

  def testNumCells(self):
    self.assertEqual(self.column.numCells(), len(LIST))

  def testGetName(self):
    self.assertEqual(self.column.getName(), COLUMN_NAME)

  def testSetFormula(self):
    self.column.setFormula(FORMULA)
    self.assertEqual(self.column._formula, FORMULA)

  def testSetTable(self):
    self.column.setTable(TABLE)
    self.assertEqual(self.column._owning_table, TABLE)

  def testUpdateCell(self):
    INDEX = 0
    new_value = LIST[INDEX] + 10
    self.column.updateCell(new_value, INDEX)
    self.assertEqual(self.column._data_values[INDEX], new_value)

  def testInsertCell(self):
    NEW_VALUE = 30
    self.column.insertCell(NEW_VALUE)
    index = len(LIST)
    self.assertEqual(self.column.getCells()[index], NEW_VALUE)


if __name__ == '__main__':
    unittest.main()

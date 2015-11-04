'''Tests for column'''

import column as cl
import unittest
import errors as er
import numpy as np
from util_test import createColumn, compareValues, toList

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
    column.addCells(SINGLE)
    self.assertTrue(compareValues(column._data_values, SINGLE))
    column = cl.Column(COLUMN_NAME)
    column.addCells(LIST)
    self.assertTrue(compareValues(column._data_values, LIST))
    column = cl.Column(COLUMN_NAME)
    column.addCells(ARRAY)
    self.assertTrue(compareValues(column._data_values, ARRAY))

  def testCopy(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    column_copy = column.copy()
    self.assertEqual(column._name, column_copy._name)
    self.assertTrue(compareValues(column._data_values, column_copy._data_values))
    self.assertEqual(column._formula, column_copy._formula)
    self.assertIsNone(column_copy._owning_table)

  def testDeleteCells(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    INDEX = 0
    NON_INDEX = 1
    column.deleteCells([INDEX])
    self.assertEqual(column._data_values[INDEX], LIST[NON_INDEX])

  def testEvaluate(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    self.assertRaises(er.NotYetImplemented, column.evaluate)

  def testGetCells(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    cells = column.getCells()
    self.assertTrue(compareValues(column._data_values, cells))

  def testNumCells(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    self.assertEqual(column.numCells(), len(LIST))

  def testGetName(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    self.assertEqual(column.getName(), column._name)

  def testSetFormula(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=None)
    column.setFormula(FORMULA)
    self.assertEqual(column._formula, FORMULA)

  def testSetTable(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=None,
        formula=FORMULA)
    column.setTable(TABLE)
    self.assertEqual(column._owning_table, TABLE)

  def testUpdateCell(self):
    column = createColumn(COLUMN_NAME, data=LIST, table=None,
        formula=FORMULA)
    INDEX = 0
    new_value = LIST[INDEX] + 10
    column.updateCell(new_value, INDEX)
    self.assertEqual(column._data_values[INDEX], new_value)
    
    


if __name__ == '__main__':
    unittest.main()

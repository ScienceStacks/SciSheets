'''Tests for column'''

import column as cl
import unittest
import errors as er
import numpy as np
from util_test import createColumn, compareValues

# Constants
COLUMN_NAME = "DUMMY"
COLUMN_STR_NAME = "DUMMY_STR"
LIST = [2.0, 3.0]
LIST1 = [20.0, 30.0]
LIST_STR = ["aa bb", "cc"]
TABLE = 'DUMMY'
VALID_FORMULA = "a + b*math.cos(x)"
INVALID_FORMULA = "a + b*math.cos(x"


#############################
# Helpers
#############################
def checkStrColumnType(column_type):
  """
  Checks the column data type
  """
  return (column_type == '|S1000') or (column_type == object)

#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestColumn(unittest.TestCase):

  def setUp(self):
    self.column = createColumn(COLUMN_NAME, data=LIST, table=None,
        formula=VALID_FORMULA)
    self.column_str = createColumn(COLUMN_STR_NAME, data=LIST_STR,
        table=None, formula=VALID_FORMULA)

  def testConstructor(self):
    column = cl.Column(COLUMN_NAME)
    self.assertEqual(column._name, COLUMN_NAME)
    self.assertIsNone(column._owning_table)
    self.assertIsNone(column._formula)

  def testAddCellsFloat(self):
    single_float = 1.0
    list_float = [2.0, 3.0]
    test_array = np.array(list_float)
    column = cl.Column(COLUMN_NAME)
    column.addCells(single_float)
    self.assertTrue(compareValues(column._data_values, single_float))
    self.assertEqual(column._data_values.dtype,
       np.float64)  # pylint: disable=E1101
    column = cl.Column(COLUMN_NAME)
    column.addCells(list_float)
    self.assertTrue(compareValues(column._data_values, list_float))
    column = cl.Column(COLUMN_NAME)
    column.addCells(test_array)
    self.assertTrue(compareValues(column._data_values, test_array))

  def testAddCellsStr(self):
    single_str = "cccc ccc"
    new_list_str = ["aa", "bbb bb"]
    test_array = np.array(new_list_str)
    column = cl.Column(COLUMN_NAME)
    column.addCells(single_str)
    self.assertTrue(compareValues(column._data_values, single_str))
    column = cl.Column(COLUMN_NAME)
    column.addCells(new_list_str)
    self.assertTrue(compareValues(column._data_values, new_list_str))
    column = cl.Column(COLUMN_NAME)
    column.addCells(test_array)
    self.assertTrue(compareValues(column._data_values, test_array))

  def testCopy(self):
    column_copy = self.column.copy()
    self.assertEqual(self.column._name, column_copy._name)
    self.assertEqual(self.column._data_values.dtype,
        column_copy._data_values.dtype)
    self.assertTrue(compareValues(self.column._data_values,
        column_copy._data_values))
    self.assertEqual(self.column._formula, column_copy._formula)
    self.assertIsNone(column_copy._owning_table)

  def testDeleteCells(self):
    valid_index = 0
    not_an_index = 1
    self.column.deleteCells([valid_index])
    self.assertEqual(self.column._data_values[valid_index], LIST[not_an_index])

  def testDataType(self):
    self.assertEqual(self.column.getDataType(), float)
    column_type = self.column_str.getDataType()
    self.assertTrue(checkStrColumnType(column_type))

  def testGetCells(self):
    cells = self.column.getCells()
    self.assertTrue(compareValues(self.column._data_values, cells))

  def testNumCells(self):
    self.assertEqual(self.column.numCells(), len(LIST))

  def testGetName(self):
    self.assertEqual(self.column.getName(), COLUMN_NAME)

  def testSetFormula(self):
    error = self.column.setFormula(VALID_FORMULA)
    self.assertIsNone(error)
    self.assertEqual(self.column._formula, VALID_FORMULA)
    error = self.column.setFormula(INVALID_FORMULA)
    self.assertIsNotNone(error)
    self.assertEqual(self.column._formula, VALID_FORMULA)

  def testSetTable(self):
    self.column.setTable(TABLE)
    self.assertEqual(self.column._owning_table, TABLE)

  def testUpdateCell(self):
    valid_index = 0
    new_value = LIST[valid_index] + 10
    self.column.updateCell(new_value, valid_index)
    self.assertEqual(self.column._data_values[valid_index], new_value)

  def testInsertCell(self):
    new_value = 30
    self.column.insertCell(new_value)
    index = len(LIST)
    self.assertEqual(self.column.getCells()[index], new_value)

  def testReplaceCells(self):
    new_array = np.array(LIST1)
    self.column.replaceCells(new_array)
    self.assertTrue((self.column._data_values == new_array).all())
    short_array = np.array(range(len(new_array) - 1))
    with self.assertRaises(er.InternalError):
      self.column.replaceCells(short_array)

  def testMakeStatementFromFormula(self):
    expr = "np.sin(3)"
    variable = "A"
    expected_stmt = "%s = %s" % (variable, expr)
    self.column._makeStatementFromFormula(expr, variable)
    self.assertEqual(self.column.getFormulaStatement(),
                     expected_stmt)
    self.column._makeStatementFromFormula(expected_stmt, variable)
    self.assertEqual(self.column.getFormulaStatement(),
                     expected_stmt)


if __name__ == '__main__':
  unittest.main()

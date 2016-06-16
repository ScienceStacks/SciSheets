'''Tests for column'''

import column as cl
from table import Table
import unittest
import errors as er
import numpy as np
from helpers_test import createColumn, compareValues
from helpers.extended_array import ExtendedArray

# Constants
COLUMN_NAME = "DUMMY"
COLUMN_STR_NAME = "DUMMY_STR"
LIST = [2.1, 3.0]
LIST1 = [20.0, 30.0]
LIST_STR = ["aa bb", "cc"]
TABLE = 'DUMMY'
VALID_FORMULA = "a + b*math.cos(x)"
INVALID_FORMULA = "a + b*math.cos(x"


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
    self.assertIsNone(column._formula_statement.getFormula())

  def testAddCellsFloat(self):
    single_float = 1.1
    list_float = [2.0, 3.0]
    test_array = np.array(list_float)
    column = cl.Column(COLUMN_NAME)
    column.addCells(single_float)
    self.assertTrue(compareValues(column._cells, single_float))
    self.assertEqual(np.array(column._cells).dtype,
       np.float64)  # pylint: disable=E1101
    column = cl.Column(COLUMN_NAME)
    column.addCells(list_float)
    self.assertTrue(compareValues(column._cells, list_float))
    column = cl.Column(COLUMN_NAME)
    column.addCells(test_array)
    self.assertTrue(compareValues(column._cells, test_array))

  def testAddCellsStr(self):
    single_str = "cccc ccc"
    new_list_str = ["aa", "bbb bb"]
    test_array = np.array(new_list_str)
    column = cl.Column(COLUMN_NAME)
    column.addCells(single_str)
    self.assertTrue(compareValues(column._cells, single_str))
    column = cl.Column(COLUMN_NAME)
    column.addCells(new_list_str)
    self.assertTrue(compareValues(column._cells, new_list_str))
    column = cl.Column(COLUMN_NAME)
    column.addCells(test_array)
    self.assertTrue(compareValues(column._cells, test_array))

  def testCopy(self):
    column_copy = self.column.copy()
    self.assertEqual(self.column._name, column_copy._name)
    self.assertEqual(np.array(self.column._cells).dtype,
        np.array(column_copy._cells).dtype)
    self.assertTrue(compareValues(self.column._cells,
        column_copy._cells))
    self.assertEqual(self.column._formula_statement.getFormula(), 
        column_copy._formula_statement.getFormula())
    self.assertEqual(self.column._data_class, 
        column_copy.getDataClass())
    self.assertEqual(self.column._asis, column_copy.getAsis())
    self.assertIsNone(column_copy._owning_table)

  def testDeleteCells(self):
    valid_index = 0
    not_an_index = 1
    self.column.deleteCells([valid_index])
    self.assertEqual(self.column._cells[valid_index], LIST[not_an_index])

  def testGetDataClass(self):
    data_class = self.column.getDataClass()
    self.assertEqual(data_class.cls, ExtendedArray)
    data_class = self.column_str.getDataClass()
    self.assertEqual(data_class.cls, ExtendedArray)

  def testGetArrayType(self):
    array_type = self.column.getArrayType()
    self.assertEqual(array_type, np.float64)
    array_type = self.column_str.getArrayType()
    self.assertTrue(str(array_type)[0:2] == '|S')

  def testGetCells(self):
    cells = self.column.getCells()
    self.assertTrue(compareValues(self.column._cells, cells))

  def testNumCells(self):
    self.assertEqual(self.column.numCells(), len(LIST))

  def testGetName(self):
    self.assertEqual(self.column.getName(), COLUMN_NAME)

  def testSetFormula(self):
    error = self.column.setFormula(VALID_FORMULA)
    self.assertIsNone(error)
    self.assertEqual(self.column._formula_statement.getFormula(), 
        VALID_FORMULA)
    error = self.column.setFormula(INVALID_FORMULA)
    self.assertIsNotNone(error)
    error = self.column.setFormula("a = sin(x")
    self.assertIsNotNone(error)

  def testSetTable(self):
    self.column.setTable(TABLE)
    self.assertEqual(self.column._owning_table, TABLE)

  def testUpdateCell(self):
    valid_index = 0
    new_value = LIST[valid_index] + 10
    self.column.updateCell(new_value, valid_index)
    self.assertEqual(self.column._cells[valid_index], new_value)

  def testInsertCell(self):
    new_value = 30
    self.column.insertCell(new_value)
    index = len(LIST)
    self.assertEqual(self.column.getCells()[index], new_value)

  def testReplaceCells(self):
    self.column.replaceCells(LIST1)
    self.assertTrue(all(
        [self.column._cells[n] == LIST1[n] for n in range(len(LIST1))]))
    short_array = np.array(range(len(LIST1) - 1))
    with self.assertRaises(er.InternalError):
      self.column.replaceCells(short_array)

  def testIsEquivalent(self):
    new_column = self.column.copy()
    self.assertTrue(self.column.isEquivalent(new_column))
    new_column.addCells(np.nan)
    self.assertTrue(self.column.isEquivalent(new_column))
    new_column = self.column.copy()
    idx = 0
    cell = self.column.getCell(idx)
    new_cell = "new_%s" % str(cell)
    self.column.updateCell(new_cell, idx)
    self.assertFalse(self.column.isEquivalent(new_column))
    new_column.updateCell(new_cell, idx)
    self.assertTrue(self.column.isEquivalent(new_column))
  
  def testIsEquivalentNans(self):
    new_column = self.column.copy()
    new_column.insertCell(np.nan)
    self.column.insertCell(np.nan)
    self.assertTrue(self.column.isEquivalent(new_column))
    new_column.insertCell(None)
    self.column.insertCell(None)
    self.assertTrue(self.column.isEquivalent(new_column))
    
  def testIsEquivalentNestedLists(self):
    table = Table("dummy")
    [column1, column2] = table.getCapture("column_is_equivalent")
    self.assertTrue(column1.isEquivalent(column2))
    [column1, column2] = table.getCapture("column_is_equivalent2")
    self.assertTrue(column1.isEquivalent(column2))

  def testPrunedCells(self):
    values = [n*1.0 for n in range(5)]
    self.column.addCells(values, replace=True)
    self.assertEqual(self.column.prunedCells(), values)
    new_values = list(values)
    new_values.append(np.nan)
    self.column.addCells(new_values, replace=True)
    self.assertEqual(self.column.prunedCells(), values)
    new_values = list(values)
    new_values.insert(0, np.nan)
    self.column.addCells(new_values, replace=True)
    self.assertEqual(self.column.prunedCells(), 
        new_values)
    


if __name__ == '__main__':
  unittest.main()

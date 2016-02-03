'''Tests for table_evaluator'''

import os
import table as tb 
import column as cl
import errors as er
import numpy as np
from table_evaluator import TableEvaluator
from util_test import createColumn, createTable
import unittest


# Constants
COLUMN = "DUMMY"
COLUMN1 = "DUMMY1"
COLUMN2 = "A"
COLUMN3 = "DUMMY3"
COLUMN4 = "DUMMY4"
COLUMN5 = "B"
COLUMNC = "C"
COLUMN_VALID_FORMULA = "VALID_FORMULA"
COLUMN_INVALID_FORMULA = "INVALID_FORMULA"
TABLE_NAME = "DUMMY_TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
VALID_FORMULA = "np.sin(A) + B"
VALID_FORMULA_WITH_USER_FUNCTION = "np.sin(A) + timesTwo(B)"
SECOND_VALID_FORMULA = "np.cos(C)"
INVALID_FORMULA = "np.cun(A)" # Invalid function
COLUMN1_CELLS = ["one", "two", "three"]
COLUMN2_CELLS = [10.0, 20.0, 30.0]
COLUMN5_CELLS = [100.0, 200.0, 300.0]
COLUMNC_CELLS = [1000.0, 2000.0, 3000.0]
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
IMPORT_PATHS = ["", "scisheets.core"]


#############################
# Tests
#############################
class TestTable(unittest.TestCase):

  def setUp(self):
    self.table = createTable(TABLE_NAME)
    self._addColumn(COLUMN1, cells=COLUMN1_CELLS)   
    self.column_a = self._addColumn(COLUMN2, cells=COLUMN2_CELLS)   
    self.column_b = self._addColumn(COLUMN5, cells=COLUMN5_CELLS)   
    self.column_c = self._addColumn(COLUMNC, cells=COLUMNC_CELLS)   
    self.column_valid_formula = self._addColumn(COLUMN_VALID_FORMULA, formula=VALID_FORMULA)
    self.te = TableEvaluator(self.table)

  def _addColumn(self, name, cells=None, formula=None):
    column = cl.Column(name)
    if formula is not None:
      column.setFormula(formula)
    if cells is not None:
      column.addCells(cells)
    self.table.addColumn(column)
    return column

  def testConstructor(self):
    te = TableEvaluator(self.table)
    self.assertEqual(te._table.getName(), TABLE_NAME)

  def testEvaluate(self):
    error = self.te.evaluate()
    self.assertIsNone(error)
    formula_result = ( 
                       np.sin(self.column_a.getCells()) 
                       + self.column_b.getCells()
                     )
    b = np.equal(formula_result, 
                 self.column_valid_formula.getCells()).all()
    self.assertTrue(b)

  def testEvaluateError(self):
    column_invalid_formula = cl.Column(COLUMN_INVALID_FORMULA)
    column_invalid_formula.setFormula(INVALID_FORMULA)
    self.table.addColumn(column_invalid_formula)
    te = TableEvaluator(self.table)
    error = te.evaluate()
    self.assertIsNotNone(error)

  def testEvaluateTwoFormulas(self):
    self.column_a.setFormula(SECOND_VALID_FORMULA)  # Make A a formula column
    te = TableEvaluator(self.table)
    error = te.evaluate()
    self.assertIsNone(error)

  def testEvaluateWithNoneValues(self):
    table = self.table
    row = table.getRow()
    table.addRow(row, 0.1)  # Add a new row after
    error = self.te.evaluate()
    self.assertIsNotNone(error)
    new_row = table.getRow()
    new_row['A'] = 1
    new_row['B'] = 1
    table.updateRow(new_row, 1)
    error = self.te.evaluate()
    self.assertIsNone(error)

  def testFindPythonFiles(self):
    this_file = os.path.split(__file__)[1]
    FILE_ABSENT = this_file # Test file shouldn't be present
    FILE_PRESENT = this_file[5:]  # File being tested should be present
    if FILE_PRESENT[-1] == 'c':
      FILE_PRESENT = FILE_PRESENT[:-1]  # Handle executing from .pyc
    python_files = TableEvaluator._findPythonFiles(CUR_DIR)
    self.assertTrue(python_files.index(FILE_PRESENT) > -1)
    with self.assertRaises(ValueError):
      python_files.index(FILE_ABSENT)

  def testEvaluateWithUserFunction(self):
    self.column_valid_formula.setFormula(VALID_FORMULA_WITH_USER_FUNCTION)
    # At most one path will work
    errors = []
    for path in IMPORT_PATHS:
      errors.append(self.te.evaluate(user_directory=CUR_DIR, import_path=path))
    self.assertTrue(errors.index(None) > -1)

  def testEvaluateFormulaWithRowAddition(self):
    # Tests a formula that should increase the number of rows.
    num_rows = self.table.numRows()
    formula = "range(%d)" % (num_rows + 1)
    self.column_valid_formula.setFormula(formula)
    self.table.evaluate()
    self.assertEqual(self.table.numRows(), num_rows + 1)

  def testEvaluateFormulaWithLargeRowAddition(self):
    # Tests a formula that should increase the number of rows.
    NUM_ROWS = 1000
    formula = "range(%d)" % NUM_ROWS
    self.column_valid_formula.setFormula(formula)
    self.table.evaluate()
    self.assertEqual(self.table.numRows(), NUM_ROWS)

  def testEvaluateRowInsert(self):
    ROW_INDEX = 1
    new_row = self.table.getRow()
    self.table.insertRow(new_row, index=ROW_INDEX)
    error = self.table.evaluate()
    self.assertIsNotNone(error)  # sin is not defined for None values
    new_row['A'] = 0.5
    new_row['B'] = 0.6
    self.table.updateRow(new_row, index=ROW_INDEX)
    error = self.table.evaluate()
    self.assertIsNone(error)  # Formula should work

  def testEvalWithMixedTypes(self):
    self.column_b.setFormula("range(len(A))")
    self.column_valid_formula.setFormula("np.sin(np.array(B, dtype=float)")
    self.table.evaluate()
    for v in self.column_valid_formula.getCells():
      if v is None:
        import pdb; pdb.set_trace()
      self.assertIsNotNone(v)

  def testExport(self):
    return
    self.table.export(function_name="my_test", 
                      output=COLUMN_VALID_FORMULA)


    


if __name__ == '__main__':
    unittest.main()

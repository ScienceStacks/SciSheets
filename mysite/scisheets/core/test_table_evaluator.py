'''Tests for table_evaluator'''

import os
import column as cl
import numpy as np
from os.path import join
import shutil
from table_evaluator import TableEvaluator
import helpers.api_util as api_util
from helpers_test import createTable, stdoutIO, TableFileHelper, \
    TEST_DIR, augmentPythonPath, runProcess
import unittest


# Constants
COLUMN = "DUMMY"
COLUMN1 = "DUMMY1"
COLUMN2 = "A"
COLUMN3 = "DUMMY3"
COLUMN4 = "DUMMY4"
COLUMNB = "B"
COLUMNC = "C"
COLUMN_VALID_FORMULA = "VALID_FORMULA"
COLUMN_INVALID_FORMULA = "INVALID_FORMULA"
COLUMN_USING_EXPORT = "E"
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
COLUMNB_CELLS = [100.0, 200.0, 300.0]
COLUMNC_CELLS = [1000.0, 2000.0, 3000.0]
IMPORT_PATHS = ["", "scisheets.core"]
FUNCTION_NAME = "myFunction"

IGNORE_TEST = False


# Ensure current directory is in the path
augmentPythonPath([__file__, 'helpers/program_generator.py'])


#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestTableEvaluator(unittest.TestCase):

  def setUp(self):
    self.table = createTable(TABLE_NAME)
    self._addColumn(COLUMN1, cells=COLUMN1_CELLS)
    self.column_a = self._addColumn(COLUMN2, cells=COLUMN2_CELLS)
    self.column_b = self._addColumn(COLUMNB, cells=COLUMNB_CELLS)
    self.column_c = self._addColumn(COLUMNC, cells=COLUMNC_CELLS)
    self.column_valid_formula = self._addColumn(COLUMN_VALID_FORMULA,
                                                formula=VALID_FORMULA)
    api_util.writeObjectToFile(self.table)
    self.evaluator = TableEvaluator(self.table)

  def _addColumn(self, name, cells=None, formula=None):
    column = cl.Column(name)
    if formula is not None:
      column.setFormula(formula)
    if cells is not None:
      column.addCells(cells)
    self.table.addColumn(column)
    return column

  def testConstructor(self):
    if IGNORE_TEST:
      return
    evaluator = TableEvaluator(self.table)
    self.assertEqual(evaluator._table.getName(), TABLE_NAME)

  def testEvaluate(self):
    #if IGNORE_TEST:
    #  return
    error = self.evaluator.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(error)
    # pylint: disable=E1101
    formula_result = (
                       np.sin(np.array(self.column_a.getCells()))
                       + np.array(self.column_b.getCells())
                     )
    is_equal = np.equal(formula_result,
                 np.array(self.column_valid_formula.getCells())).all()
    self.assertTrue(is_equal)

  def testEvaluateError(self):
    if IGNORE_TEST:
      return
    column_invalid_formula = cl.Column(COLUMN_INVALID_FORMULA)
    column_invalid_formula.setFormula(INVALID_FORMULA)
    self.table.addColumn(column_invalid_formula)
    evaluator = TableEvaluator(self.table)
    error = evaluator.evaluate(user_directory=TEST_DIR)
    self.assertIsNotNone(error)

  def testEvaluateTwoFormulas(self):
    if IGNORE_TEST:
      return
    self.column_a.setFormula(SECOND_VALID_FORMULA)  # Make A a formula column
    evaluator = TableEvaluator(self.table)
    error = evaluator.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(error)

  def testEvaluateWithNoneValues(self):
    if IGNORE_TEST:
      return
    table = self.table
    row = table.getRow()
    table.addRow(row, 0.1)  # Add a new row after
    error = self.evaluator.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(error)
    new_row = table.getRow()
    new_row['A'] = 1
    new_row['B'] = 1
    table.updateRow(new_row, 1)
    error = self.evaluator.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(error)

  def testEvaluateWithUserFunction(self):
    if IGNORE_TEST:
      return
    self.column_valid_formula.setFormula(VALID_FORMULA_WITH_USER_FUNCTION)
    errors = self.evaluator.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(errors)

  def testEvaluateFormulaWithRowAddition(self):
    if IGNORE_TEST:
      return
    # Tests a formula that should increase the number of rows.
    num_rows = self.table.numRows()
    formula = "range(%d)" % (num_rows + 1)
    self.column_valid_formula.setFormula(formula)
    self.table.evaluate(user_directory=TEST_DIR)
    self.assertEqual(self.table.numRows(), num_rows + 1)

  def testEvaluateFormulaWithLargeRowAddition(self):
    if IGNORE_TEST:
      return
    # Tests a formula that should increase the number of rows.
    num_rows = 1000
    formula = "range(%d)" % num_rows
    self.column_valid_formula.setFormula(formula)
    self.table.evaluate(user_directory=TEST_DIR)
    self.assertEqual(self.table.numRows(), num_rows)

  def testEvaluateRowInsert(self):
    if IGNORE_TEST:
      return
    row_index = 1
    new_row = self.table.getRow()
    self.table.insertRow(new_row, index=row_index)
    error = self.table.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(error)
    new_row['A'] = 0.5
    new_row['B'] = 0.6
    self.table.updateRow(new_row, index=row_index)
    error = self.table.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(error)  # Formula should work

  def testEvalWithMixedTypes(self):
    if IGNORE_TEST:
      return
    self.column_b.setFormula("range(len(A))")
    self.column_valid_formula.setFormula("np.sin(np.array(B, dtype=float))")
    self.table.evaluate(user_directory=TEST_DIR)
    for val in self.column_valid_formula.getCells():
      self.assertIsNotNone(val)

  def _createExport(self, function_name, no_outputs=2):
    # Two formula columns
    self.column_a.setFormula(SECOND_VALID_FORMULA)  # Make A a formula column
    self.table.evaluate(user_directory=TEST_DIR)
    if no_outputs == 2:
      outputs=[COLUMN_VALID_FORMULA, COLUMN2]
    else:
      outputs=[COLUMN_VALID_FORMULA]
    self.table.export(function_name=function_name,
                      inputs=[COLUMNC, COLUMNB],
                      outputs=outputs,
                      user_directory=TEST_DIR)

  def testExport(self):
    if IGNORE_TEST:
      return
    # Two formula columns
    self._createExport(FUNCTION_NAME)
    file_name = "%s.py" % FUNCTION_NAME
    file_path = join(TEST_DIR, file_name)
    test_file_name = "test_%s.py" % FUNCTION_NAME
    test_file_path = join(TEST_DIR, test_file_name)
    try:
      with stdoutIO():
        execfile(file_path)
      success = True
    except IOError:
      success = False
    self.assertTrue(success)
    # Run the program and its test. Will get an exception if these fail.
    commands = """
        cd $HOME/SciSheets/mysite; 
        python manage.py test scisheets.core.test_dir.%s
        """ % FUNCTION_NAME
    out = runProcess(commands)
    test_commands = """
        cd $HOME/SciSheets/mysite; 
        python manage.py test scisheets.core.test_dir.test_%s
        """ % FUNCTION_NAME
    test_out = runProcess(test_commands)

  def testUsingExport(self):
    self._createExport(FUNCTION_NAME, no_outputs=1)
    # Create a column that uses this function
    formula = "%s(%s, %s)" % (FUNCTION_NAME, COLUMNC, COLUMNB)
    column_using_export = self._addColumn(COLUMN_USING_EXPORT,
                                          formula=formula)
    error = self.evaluator.evaluate(user_directory=TEST_DIR)
    self.assertEqual(column_using_export.getCells(),
                     self.column_valid_formula.getCells())

  @staticmethod
  def _countNonNone(aList):
    return len([x for x in aList if (x is not None)
        and (not np.isnan(x))])  # pylint: disable=E1101

  def _testFormulaVariations(self, formula1, formula2, len1, len2):
    # Checks compound formulas of different combinations.
    # Input: formula1 - valid python expression
    #        formula2 - valid python statement for column A or ""
    #        len1 - length of the array created by formula1
    #        len2 - length of the array created by formula2
    if len(formula2) == 0:
      formula = formula1
      self.column_valid_formula.setFormula(formula)
      error = self.evaluator.evaluate(user_directory=TEST_DIR)
      if error is not None:
        import pdb; pdb.set_trace()
      self.assertIsNone(error)
      self.assertEqual(
          TestTableEvaluator._countNonNone(
          self.column_valid_formula.getCells()), len1)
    else:
      formula = "%s; %s" % (formula1, formula2)
      self.column_valid_formula.setFormula(formula)
      self.assertIsNone(self.evaluator.evaluate(user_directory=TEST_DIR))
      self.assertEqual(
          TestTableEvaluator._countNonNone(
          self.column_valid_formula.getCells()), len1)
      self.assertEqual(
          TestTableEvaluator._countNonNone(self.column_a.getCells()),
          len2)

  def testFormulaVariations(self):
    if IGNORE_TEST:
      return
    size = 10
    list_expr = "[n for n in range(%d)]" % size
    scalar_expr = "np.sin(3.1)"
    list_stmt = "A = np.array([n for n in range(%d)])" % size
    list_stmt1 = "VALID_FORMULA = np.array([n for n in range(%d)])" % size
    scalar_stmt = "A = np.sin(3.1)"
    scalar_stmt1 = "VALID_FORMUAL = np.sin(3.1)"
    self._testFormulaVariations(list_expr, "", size, 0)
    self._testFormulaVariations(scalar_expr, "", 1, 0)
    self._testFormulaVariations(list_stmt, scalar_stmt, 1, 1)
    self._testFormulaVariations(scalar_stmt1, scalar_stmt, 1, 1)
    self._testFormulaVariations(list_stmt1, list_stmt, size, size)

  def testDefinedFunctionInFormula(self):
    if IGNORE_TEST:
      return
    formula = '''
def is_prime(n):
    limit = int(mt.sqrt(n)) + 1
    for m in range(2, limit):
      if n % m == 0:
        return False
    return True
def find_primes(n):
  result = []
  for m in range(2, n):
    if is_prime(m):
      result.append(m)
  return result
DUMMY1 = find_primes(100)
'''
    self.column_valid_formula.setFormula(formula)
    errors = self.evaluator.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(errors)


if __name__ == '__main__':
  unittest.main()

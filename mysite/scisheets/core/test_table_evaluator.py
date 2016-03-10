'''Tests for table_evaluator'''

import os
import column as cl
import numpy as np
from os.path import join
import shutil
from table_evaluator import TableEvaluator
from util_test import createTable, stdoutIO, TableFileHelper
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
TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'test_dir')
IMPORT_PATHS = ["", "scisheets.core"]


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
    filename = "dummy"
    helper = TableFileHelper(filename, TEST_DIR)
    helper.create()
    python_files = TableEvaluator._findFilenames(TEST_DIR)
    self.assertTrue(python_files.index(filename) > -1)
    helper.destroy()

  def testEvaluateWithUserFunction(self):
    self.column_valid_formula.setFormula(VALID_FORMULA_WITH_USER_FUNCTION)
    errors = self.te.evaluate(user_directory=TEST_DIR)
    self.assertIsNone(errors)

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
    # Two formula columns
    function_name = "my_test"
    file_name = "%s.py" % function_name
    file_path = join(TEST_DIR, file_name)
    self.column_a.setFormula(SECOND_VALID_FORMULA)  # Make A a formula column
    self.table.evaluate()
    self.table.export(function_name=function_name,
                      file_path = file_path,
                      user_directory = TEST_DIR,
                      inputs=[COLUMNC, COLUMN5],
                      outputs=[COLUMN_VALID_FORMULA, COLUMN2])
    try:
      with stdoutIO():
        execfile(file_path)
      success = True
    except IOError:
      success = False
    self.assertTrue(success)
    try:
      os.remove("/tmp/%s" % file_name)  # Delete the file created
    except OSError:
      pass
    shutil.move(file_path, "/tmp")  # Put in temp

  def testMechaelisMenton(self):
    return
    self.table = createTable("MechaelisMenton")
    self._addColumn("THDPA", cells=[0.01, 0.05, 0.12, 0.2, 0.5, 1.0])
    self._addColumn("V", cells=[0.110, 0.19, 0.21, 0.22, 0.21, 0.24])
    self._addColumn("INV_THDPA", formula = "1/THDPA")
    self._addColumn("INV_V", formula = "1/V")
    self._addColumn("INTERCEPT", formula = "intercept(INV_THDPA, INV_V)")
    self._addColumn("SLOPE", formula = "slope(INV_THDPA, INV_V)")
    self._addColumn("Vmax", formula = "1/INTERCEPT")
    self._addColumn("KM", formula="Vmax*SLOPE")
    self.table.export(function_name="MechaelisMenton",
                      inputs=["THDPA", "V"],
                      outputs=["Vmax", "KM"])
 
  @staticmethod 
  def _countNonNone(array):
    return len([x for x in array if x is not None])

  def _testFormulaVariations(self, formula1, formula2, len1, len2):
     # Checks compound formulas of different combinations.
     # Input: formula1 - valid python expression
     #        formula2 - valid python statement for column A or ""
     #        len1 - length of the array created by formula1
     #        len2 - length of the array created by formula2
     if len(formula2) == 0:
       formula = formula1
       self.column_valid_formula.setFormula(formula)
       self.assertIsNone(self.te.evaluate())
       self.assertEqual(
           TestTableEvaluator._countNonNone(self.column_valid_formula.getCells()), 
                        len1)
     else:
       formula = "%s; %s" % (formula1, formula2)
       self.column_valid_formula.setFormula(formula)
       self.assertIsNone(self.te.evaluate())
       self.assertEqual(
           TestTableEvaluator._countNonNone(self.column_valid_formula.getCells()), 
                        len1)
       self.assertEqual(
           TestTableEvaluator._countNonNone(self.column_a.getCells()), 
           len2)
    

  def testFormulaVariations(self):
    # TODO: Need test that checks no changing current column if I have a statement
    #       assigning to another column
    size = 10
    list_expr = "[n for n in range(%d)]" % size
    scalar_expr = "np.sin(3.1)"
    LIST_STMT = "A = np.array([n for n in range(%d)])" % size
    LIST_STMT1 = "VALID_FORMULA = np.array([n for n in range(%d)])" % size
    SCALAR_STMT = "A = np.sin(3.1)"
    SCALAR_STMT1 = "VALID_FORMUAL = np.sin(3.1)"
    self._testFormulaVariations(list_expr, "", size, 0)
    self._testFormulaVariations(scalar_expr, "", 1, 0)
    self._testFormulaVariations(LIST_STMT, SCALAR_STMT, 1, 1)
    self._testFormulaVariations(SCALAR_STMT1, SCALAR_STMT, 1, 1)
    self._testFormulaVariations(LIST_STMT1, LIST_STMT, size, size)
    

if __name__ == '__main__':
    unittest.main()

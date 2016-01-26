'''Tests for table_evaluator'''

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
COLUMN_VALID_FORMULA = "VALID_FORMULA"
COLUMN_INVALID_FORMULA = "INVALID_FORMULA"
TABLE_NAME = "DUMMY_TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
VALID_FORMULA = "n.sin(A) + B"
INVALID_FORMULA = "n.cun(A)" # Invalid function
COLUMN1_CELLS = ["one", "two", "three"]
COLUMN2_CELLS = [10.0, 20.0, 30.0]
COLUMN5_CELLS = [100.0, 200.0, 300.0]


#############################
# Tests
#############################
class TestTable(unittest.TestCase):

  def setUp(self):
    self.table = createTable(TABLE_NAME)
    column1 = cl.Column(COLUMN1)
    column1.addCells(COLUMN1_CELLS)
    self.table.addColumn(column1)
    column2 = cl.Column(COLUMN2)
    column2.addCells(COLUMN2_CELLS)
    self.table.addColumn(column2)
    self.column_a = column2
    column5 = cl.Column(COLUMN5)
    column5.addCells(COLUMN5_CELLS)
    self.column_b = column5
    self.table.addColumn(column5)
    self.columns = self.table.getColumns()
    column_valid_formula = cl.Column(COLUMN_VALID_FORMULA)
    column_valid_formula.setFormula(VALID_FORMULA)
    self.table.addColumn(column_valid_formula)
    self.column_valid_formula = column_valid_formula
    self.te = TableEvaluator(self.table)

  def testConstructor(self):
    te = TableEvaluator(self.table)
    self.assertEqual(te.table.getName(), TABLE_NAME)

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


if __name__ == '__main__':
    unittest.main()

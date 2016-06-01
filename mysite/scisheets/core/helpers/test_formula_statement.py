'''Tests for column'''

from formula_statement import FormulaStatement
from scisheets.core.helpers_test import createColumn, compareValues
import unittest

# Constants
COLUMN_NAME = "DUMMY"
COLUMN_STR_NAME = "DUMMY_STR"
LIST = [2.1, 3.0]
LIST1 = [20.0, 30.0]
LIST_STR = ["aa bb", "cc"]
TABLE = 'DUMMY'
VALID_FORMULA = "a + b*math.cos(x)"
INVALID_FORMULA = "a + b*math.cos(x"


#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestFormulaStatement(unittest.TestCase):
  
  def setUp(self):
    self.column = createColumn(COLUMN_NAME, data=LIST)
    self.fs = FormulaStatement(VALID_FORMULA, self.column)
    self.invalid_fs = FormulaStatement(INVALID_FORMULA, self.column)

  def testDo(self):
    error = self.fs.do()
    self.assertIsNone(error)
    error = self.invalid_fs.do()
    self.assertIsNotNone(error)

  def testGetStatement(self):
    self.fs.do()
    statement = self.fs.getStatement()
    expected_statement = "%s = %s" % (COLUMN_NAME, VALID_FORMULA)
    self.assertEqual(statement, expected_statement)

  def testGetFormula(self):
    self.assertEqual(VALID_FORMULA, self.fs.getFormula())

  def testExpression(self):
    fs = FormulaStatement(VALID_FORMULA, self.column)
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 1)
    self.assertTrue(fs.isExpression())

  def testStatement(self):
    formula = "%s = %s" % (self.column.getName(), VALID_FORMULA)
    fs = FormulaStatement(formula, self.column)
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 1)
    self.assertFalse(fs.isExpression())

  def testAmbiguousStatement(self):
    formula = "s.initialize()"
    fs = FormulaStatement(formula, self.column)
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 1)
    self.assertTrue(fs.isExpression())

  def testMultilineStatement(self):
    formula = """
s.initialize()
s.go()
"""
    fs = FormulaStatement(formula, self.column)
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 0)
    self.assertFalse(fs.isExpression())

  def testSemicolonStatement(self):
    formula = "s.initialize();s.go()"
    fs = FormulaStatement(formula, self.column)
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 0)
    self.assertFalse(fs.isExpression())

  def testSemicolonOneStatement(self):
    formula = "s.initialize();"
    fs = FormulaStatement(formula, self.column)
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 0)
    self.assertFalse(fs.isExpression())
    

if  __name__ == '__main__':
  unittest.main()

'''Tests for FormulaStatement'''

from scisheets.core.helpers.formula_statement import FormulaStatement
from scisheets.core.helpers_test import createColumn, compareValues
import unittest

# Constants
COLUMN_NAME = "DUMMY"
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
    self.fs = FormulaStatement(VALID_FORMULA, COLUMN_NAME)
    self.invalid_fs = FormulaStatement(INVALID_FORMULA, "INVALID")

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
    fs = FormulaStatement(VALID_FORMULA, "TEST_FORMULA")
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 1)
    self.assertTrue(fs.isExpression())

  def testStatement(self):
    formula = "%s = %s" % ("TEST_FORMULA", VALID_FORMULA)
    fs = FormulaStatement(formula, "TEST_FORMULA")
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 1)
    self.assertFalse(fs.isExpression())

  def testAmbiguousStatement(self):
    formula = "s.initialize()"
    fs = FormulaStatement(formula, "TEST_FORMULA")
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 1)
    self.assertTrue(fs.isExpression())

  def testMultilineStatement(self):
    formula = """
s.initialize()
s.go()
"""
    fs = FormulaStatement(formula, "TEST_FORMULA")
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 0)
    self.assertFalse(fs.isExpression())

  def testSemicolonStatement(self):
    formula = "s.initialize();s.go()"
    fs = FormulaStatement(formula, "TEST_FORMULA")
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 0)
    self.assertFalse(fs.isExpression())

  def testSemicolonOneStatement(self):
    formula = "s.initialize();"
    fs = FormulaStatement(formula, "TEST_FORMULA")
    self.assertIsNone(fs.do())
    self.assertEqual(fs.getStatement().count("="), 0)
    self.assertFalse(fs.isExpression())

  def testIsEquivalent(self):
    formula_statement = FormulaStatement(VALID_FORMULA, COLUMN_NAME)
    self.assertTrue(self.fs.isEquivalent(formula_statement))
    self.assertFalse(self.fs.isEquivalent(self.invalid_fs))
    

if  __name__ == '__main__':
  unittest.main()

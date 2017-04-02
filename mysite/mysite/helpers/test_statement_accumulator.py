'''
Tests for statement accumulator.
 '''

from mysite.helpers.statement_accumulator import StatementAccumulator
from scisheets.core import helpers_test as ht
import unittest


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestStatementAccumulator(unittest.TestCase):

  def setUp(self):
    self.sa = StatementAccumulator()

  def testAdd(self):
    statement = "This is a test."
    self.sa.add(statement)
    self.assertEqual(self.sa._statements[0], statement)
    statement = "This is another test."
    self.sa.add(statement)
    self.assertEqual(self.sa._statements[1], statement)

  def testAddWithIndent(self):
    statement = "This is a test."
    self.sa.add(statement)
    self.sa.indent(1)
    statement = "This is another test."
    self.sa.add(statement)
    self.assertEqual(self.sa._statements[1], "  %s" % statement)
    self.sa.indent(1)
    statement = "This is another test."
    self.sa.add(statement)
    self.assertEqual(self.sa._statements[2], "    %s" % statement)
    self.sa.indent(-1)
    statement = "This is another test."
    self.sa.add(statement)
    self.assertEqual(self.sa._statements[3], "  %s" % statement)

  def testGet(self):
    first_statement = "This is a test."
    self.sa.add(first_statement)
    self.assertEqual(self.sa.get(), first_statement)
    self.sa.indent(1)
    second_statement = "This is a test."
    self.sa.add(second_statement)
    expected_result ="%s\n  %s" % (first_statement, second_statement)
    self.assertEqual(self.sa.get(), expected_result)

  def testExtra(self):
    statement = '''# Evaluation of the table %s.

    ''' % "aName"
    self.sa.add(statement)


if __name__ == '__main__':
  unittest.main()

'''Tests for program runner.'''

from scisheets.core import column as cl
from scisheets.core.helpers.program_runner import ProgramRunner
from scisheets.core.helpers_test import createTable, stdoutIO, TableFileHelper, \
    TEST_DIR, augmentPythonPath
from scisheets.core.helpers.api_util import writeObjectToFile
import numpy as np
import os
import shutil
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
IMPORT_PATHS = ["", "scisheets.core"]
TEST_TEXT_FILE = "test_file"
TEST_TEXT_PATH = os.path.join(TEST_DIR, "%s.py" % TEST_TEXT_FILE)
TEST_PROGRAM_FILE = "test_file"
TEST_PROGRAM_PATH = os.path.join(TEST_DIR, 
    "%s.py" % TEST_PROGRAM_FILE)
TEST_LINES = "test"
TEST_PROGRAM = """
fd = open('%s', "w")
fd.writelines('%s')
fd.close()
""" % (TEST_TEXT_PATH, TEST_LINES)


# Ensure that the current directory is in the path
augmentPythonPath(__file__)


#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestProgramRunner(unittest.TestCase):

  def setUp(self):
    self.table = createTable(TABLE_NAME)
    self._addColumn(COLUMN1, cells=COLUMN1_CELLS)
    self.column_a = self._addColumn(COLUMN2, cells=COLUMN2_CELLS)
    self.column_b = self._addColumn(COLUMN5, cells=COLUMN5_CELLS)
    self.column_c = self._addColumn(COLUMNC, cells=COLUMNC_CELLS)
    self.column_valid_formula = self._addColumn(COLUMN_VALID_FORMULA,
                                                formula=VALID_FORMULA)

  def _addColumn(self, name, cells=None, formula=None):
    column = cl.Column(name)
    if formula is not None:
      column.setFormula(formula)
    if cells is not None:
      column.addCells(cells)
    self.table.addColumn(column)
    return column

  def _evaluateRunnerExecution(self, 
                               error, 
                               expected_lines=TEST_LINES):
    """
    Evaluates the results of a runner execution.
    The runner executes TEST_PROGRAM, which writes to a file.
    :param str error: error from runner execution
    :param str expected_lines: lines expected to be written
    :sideeffect: removes the file created
    """
    self.assertIsNone(error)
    self.assertTrue(os.path.exists(TEST_TEXT_PATH))
    with open(TEST_TEXT_PATH, 'r') as infile:
      self.assertEqual(infile.read(), expected_lines)
    os.remove(TEST_TEXT_PATH)

  def testSimpleExecute(self):
    runner = ProgramRunner(TEST_PROGRAM, 
                           self.table,
                           user_directory=TEST_DIR,
                           program_filename=TEST_TEXT_FILE)
    self._evaluateRunnerExecution(runner.execute())

  def testWriteFile(self):
    runner = ProgramRunner(TEST_PROGRAM, 
                           self.table,
                           user_directory=TEST_DIR,
                           program_filename=TEST_TEXT_FILE)
    self._evaluateRunnerExecution(runner.writeFiles(),
                                  expected_lines=TEST_PROGRAM)

  def testExecuteWithAPIObject(self):
    writeObjectToFile(self.table)
    runner = ProgramRunner(TEST_PROGRAM, 
                           self.table,
                           user_directory=TEST_DIR,
                           program_filename=TEST_PROGRAM_FILE)
    column = self.table.columnFromName("VALID_FORMULA",
        is_relative=False)
    column.setFormula(TEST_PROGRAM)
    error = runner.execute(create_API_object=True)
    self._evaluateRunnerExecution(error)


if __name__ == '__main__':
  unittest.main()

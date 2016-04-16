'''Tests for program runner.'''

from ...core import column as cl
from program_runner import ProgramRunner
from ..helpers_test import createTable, stdoutIO, TableFileHelper, \
    TEST_DIR
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

  def testExecute(self):
    return
    test_file = "test_file.txt"
    statements = """
import os
path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'test_dir/test_program_runner.txt')
fd = open(path, "w")
fd.writelines("test")
fd.close()
"""
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
       'test_dir/test_program_runner.txt')
    runner = ProgramRunner(statements)
    runner.execute()
    self.assertTrue(os.path.exists(path))
    os.remove(path)


if __name__ == '__main__':
  unittest.main()

'''Tests for Program Executer.'''

from program_executer import ProgramExecuter, CONTROLLER
import os
import unittest


GOOD_PROGRAM = """import numpy as np  # Line 1
a = np.cos(np.pi)  # Line 2
b = range(10)  # Line 3
c = [a*n for n in b]  # Line 4
"""
EXPECTED_C = [-n for n in range(10)]
RUNTIME_ERROR_PROGRAM = """import numpy as np  # Line 1
a = np.cxs(np.pi)  # Line 2 - unknown function
b = range(10)  # Line 3
c = [a*n for n in b]  # Line 4
"""
COMPILE_ERROR_PROGRAM = """import numpy as np  # Line 1
a   np.cos(np.pi)  # Line 2
b = range 10)  # Line 3
c = [a*n for n in b]  # Line 4
"""

IGNORE_TEST = False



#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestProgramExecuter(unittest.TestCase):

  def setUp(self):
    self.namespace = {}

  def _runProgram(self, program_name, program, exc_lineno):
    """
    Executes the program.
    :param str program_name:
    :param str program:
    :param int exc_lineno: line number of exception (0 if None)
    :return str: message from syntax checking and program execution
    """
    executer = ProgramExecuter(program_name, program,
        self.namespace)
    msg = executer.execute()
    if msg is None:
      msg = executer.execute()
      if exc_lineno == 0:
        self.assertIsNone(msg)
      else:
        self.assertTrue(str(exc_lineno) in msg)
    return msg

  def testGoodProgram(self):
    if IGNORE_TEST:
      return
    self._runProgram('GOOD', GOOD_PROGRAM, 0)
    result = self.namespace['c']
    self.assertTrue(result, EXPECTED_C)

  def testExceptions(self):
    if IGNORE_TEST:
      return
    self._runProgram('RUNTIME_ERROR', RUNTIME_ERROR_PROGRAM, 2)
    self._runProgram('COMPILE_ERROR', COMPILE_ERROR_PROGRAM, 3)
    

if  __name__ == '__main__':
  unittest.main()

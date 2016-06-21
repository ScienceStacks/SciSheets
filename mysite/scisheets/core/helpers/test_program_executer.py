'''Tests for Program Executer.'''

from program_executer import ProgramExecuter
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
b = range(10)  # Line 3
c = [a*n for n in b]  # Line 4
"""



#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestProgramExecuter(unittest.TestCase):

  def setUp(self):
    self.namespace = {}

  def testGoodProgram(self):
    executer = ProgramExecuter('GOOD', 
        GOOD_PROGRAM, self.namespace)
    executer.execute()
    result = self.namespace['c']
    self.assertTrue(result, EXPECTED_C)
    self.assertIsNone(executer.getException())

  def testRuntimeError(self):
    executer = ProgramExecuter('RUNTIME_ERROR', 
        RUNTIME_ERROR_PROGRAM, self.namespace)
    executer.execute()
    self.assertIsNotNone(executer.getBlockExecutionController().getException())
    msg = executer.formatError()
    import pdb; pdb.set_trace()
    self.assertTrue('2' in msg)
    

if  __name__ == '__main__':
  unittest.main()

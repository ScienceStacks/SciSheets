'''Tests for BlockExecutionController'''

from block_execution_controller import BlockExecutionController
from scisheets.core import api as api
from mysite import settings
from scisheets.core.helpers.api_util import getTableFromFile
import os
import unittest

# Constants
TEST_TABLE_FILE = os.path.join(settings.SCISHEETS_TEST_DIR,
    "test_block_execution_controller_1.pcl")
NAME = "test"



#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestBlockExecutionController(unittest.TestCase):
  
  def setUp(self):
    self.table = getTableFromFile(TEST_TABLE_FILE, verify=False)
    self.api = api.APIFormulas(self.table)

  def testConstructor(self):
    self.assertEqual(self.api, self.api.controller._api)

  def testStartBlock(self):
    self.api.controller.startBlock(NAME)
    self.assertEqual(NAME, self.api.controller._block_name)

  def testEndBlock(self):
    self.api.controller.endBlock()
    self.assertIsNone(self.api.controller._block_name)

  def _exceptionForBlock(self, new_filename=None):
    """
    Creates an exception. Optionally changes the caller file.
    :param str new_filename:
    :returns Exception:
    """
    error = None
    self.api.controller.startBlock(NAME)
    if new_filename is None:  # Line 1
      new_filename = self.api.controller._caller_filename  # Line 2
    self.api.controller._caller_filename = new_filename  # Line 3
    try:  # Line 4
      raise RuntimeError("Testing")  # Line 5
    except RuntimeError as err:
      error = err
      self.api.controller.exceptionForBlock(err)
    return error

  def testExceptionForBlock(self):
    error = self._exceptionForBlock()
    self.assertIsNotNone(error)
    self.assertEqual(self.api.controller._block_linenumber, 5)

  def testExceptionForBlockDifferentFile(self):
    error = self._exceptionForBlock(new_filename='x')
    self.assertIsNotNone(error)
    self.assertNotEqual(self.api.controller._block_linenumber, 5)

  def testFormatError(self):
    _ = self._exceptionForBlock()
    msg = self.api.controller.formatError()
    self.assertTrue('scisheet' in msg)
    _ = self._exceptionForBlock(new_filename='x')
    msg = self.api.controller.formatError()
    self.assertTrue('file' in msg)

  def testLoopControls(self):
    self.api.controller.initializeLoop()
    self.assertFalse(self.api.controller.isTerminateLoop())
    self.api.controller.startAnIteration()
    self.api.controller.endAnIteration()
    self.assertTrue(self.api.controller.isTerminateLoop())

  def testGetException(self):
    error = self._exceptionForBlock()
    self.assertEqual(error, self.api.controller.getException())
    

if  __name__ == '__main__':
  unittest.main()

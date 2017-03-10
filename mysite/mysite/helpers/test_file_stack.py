'''Tests for FileStack'''

import unittest
from mysite.helpers.file_stack import FileStack
import os
import shutil

TEST_DIR = "/tmp/file_stack"
TEST_FILENAME = "file_stack"
TEST_FILEPATH = "/tmp/%s.txt" % TEST_FILENAME
FILENAME_PFX = "%s.t" % TEST_FILENAME
MAX_DEPTH = 5

############### FUNCTIONS ####################
def writeFile(filepath, value):
  fh = open(filepath, "w")
  fh.write("%d" % value)
  fh.close()

def checkFilepathValue(filepath, expected_value):
  fh = open(filepath, "r")
  value = fh.readline()
  if str(expected_value) != value:
    import pdb; pdb.set_trace()
  return str(expected_value) == value


############### CLASSES ####################
class TestFileStack(unittest.TestCase):

  def setUp(self):
    if os.path.exists(TEST_DIR):
      shutil.rmtree(TEST_DIR)
    os.mkdir(TEST_DIR)
    self._writeManagedFile(0)
    self.stack = FileStack(TEST_DIR, FILENAME_PFX, 
         max_depth=MAX_DEPTH)

  def _writeManagedFile(self, value):
    writeFile(TEST_FILEPATH, value)

  def _populateStack(self, size):
    """
    Creates the specified number of files in the stack
    with values 1 through size.
    :param int size: number of stack files to create
    """
    for idx in range(1, size+1):
      filepath = self.stack._makeFilepath(idx)
      writeFile(filepath, idx)

  def testMakeFilepath(self):
    filepath = self.stack._makeFilepath(1)
    self.assertEqual(filepath, "/tmp/file_stack/file_stack.t01")
    filepath = self.stack._makeFilepath(10)
    self.assertEqual(filepath, "/tmp/file_stack/file_stack.t10")

  def testGetFilepaths(self):
    filepaths = self.stack._getFilepaths()
    self.assertEqual(len(filepaths), 0)
    self._populateStack(MAX_DEPTH)
    filepaths = self.stack._getFilepaths()
    self.assertEqual(len(filepaths), MAX_DEPTH)
    filepath = self.stack._makeFilepath(3)
    # Removing the 3rd file should cause files, 4, 5 to be deleted
    os.remove(filepath)
    filepaths = self.stack._getFilepaths()
    self.assertEqual(len(filepaths), 2)
    for sfx in range(3, MAX_DEPTH+1):
      filepath = self.stack._makeFilepath(sfx)
      self.assertFalse(os.path.exists(filepath))

  def testGetTop(self):
    filepath = self.stack._getTop()
    self.assertIsNone(filepath)
    self._populateStack(MAX_DEPTH)
    filepath = self.stack._getTop()
    expected_filepath = self.stack._makeFilepath(1)
    self.assertEqual(filepath, expected_filepath)

  def testClear(self):
    self._populateStack(MAX_DEPTH)
    filepaths = self.stack._getFilepaths()
    self.assertEqual(len(filepaths), MAX_DEPTH)
    self.stack.clear()
    filepaths = self.stack._getFilepaths()
    self.assertEqual(len(filepaths), 0)

  def _testAdjustStackDown(self, size):
    self.stack.clear()
    self._populateStack(size)
    self.stack._adjustStack(is_move_down=True)
    filepaths = self.stack._getFilepaths()
    if size > 0:
      limit = min(size+1, MAX_DEPTH)
    else:
      limit = 0
    self.assertEqual(len(filepaths), limit)
    for idx in range(2, size+1):
      filepath = self.stack._makeFilepath(idx)
      self.assertTrue(checkFilepathValue(filepath, idx-1))

  def testAdjustStackDown(self):
    self._testAdjustStackDown(MAX_DEPTH-1)
    self._testAdjustStackDown(MAX_DEPTH)
    self._testAdjustStackDown(0)
    self._testAdjustStackDown(2)

  def _testAdjustStackUp(self, size):
    self.stack.clear()
    self._populateStack(size)
    self.stack._adjustStack(is_move_down=False)
    filepaths = self.stack._getFilepaths()
    limit = max(0, size - 1)
    self.assertEqual(len(filepaths), limit)
    for idx in range(1, size-1):
      filepath = self.stack._makeFilepath(idx)
      self.assertTrue(checkFilepathValue(filepath, idx+1))

  def testAdjustStackUp(self):
    self._testAdjustStackUp(0)
    self._testAdjustStackUp(MAX_DEPTH)
    self._testAdjustStackUp(1)

  def testGetDepth(self):
    self._populateStack(0)
    self.assertEqual(self.stack.getDepth(), 0)
    self.stack.clear()
    self._populateStack(MAX_DEPTH)
    self.assertEqual(self.stack.getDepth(), MAX_DEPTH)
    self.stack.clear()
    self._populateStack(1)
    self.assertEqual(self.stack.getDepth(), 1)

  def testIsEmpty(self):
    self.assertTrue(self.stack.isEmpty())
    self._populateStack(1)
    self.assertFalse(self.stack.isEmpty())
    self._populateStack(MAX_DEPTH)
    self.assertFalse(self.stack.isEmpty())
    self.stack.clear()
    self.assertTrue(self.stack.isEmpty())

  def _testPop(self, size):
    self.stack.clear()
    self._populateStack(size)
    self.stack.pop(TEST_FILEPATH)
    self.assertTrue(checkFilepathValue(TEST_FILEPATH, 1))
    filepaths = self.stack._getFilepaths()
    limit = max(0, size-1)
    self.assertEqual(len(filepaths), limit)
    for idx in range(1, size):
      filepath = self.stack._makeFilepath(idx)
      self.assertTrue(checkFilepathValue(filepath, idx+1))

  def testPop(self):
    self._testPop(2)
    with self.assertRaises(ValueError):
      self._testPop(0)
    self._testPop(MAX_DEPTH)

  def _testPush(self, size):
    self.stack.clear()
    self._populateStack(size)
    self.stack.push(TEST_FILEPATH)
    self.assertTrue(checkFilepathValue(TEST_FILEPATH, 0))
    filepaths = self.stack._getFilepaths()
    limit = min(MAX_DEPTH, size+1)
    self.assertEqual(len(filepaths), limit)
    for idx in range(1, size):
      filepath = self.stack._makeFilepath(idx)
      self.assertTrue(checkFilepathValue(filepath, idx-1))

  def testPush(self):
    self._testPush(2)
    self._testPush(0)
    self._testPush(MAX_DEPTH)
    

if __name__ == '__main__':
    unittest.main()

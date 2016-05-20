'''Tests for VersionedFile'''

import unittest
from versioned_file import VersionedFile
from test_file_stack import writeFile, checkFilepathValue
import os
import shutil

TEST_DIR = "/tmp/versioned_file"
MANAGED_FILE = "/tmp/versioned_file.txt"
MAX_DEPTH = 5


class TestVersionedFile(unittest.TestCase):

  def setUp(self):
    if os.path.exists(TEST_DIR):
      shutil.rmtree(TEST_DIR)
    os.mkdir(TEST_DIR)
    self._writeManagedFile(0)
    self.versioned = VersionedFile(MANAGED_FILE, TEST_DIR, MAX_DEPTH)

  def _writeManagedFile(self, value):
    writeFile(MANAGED_FILE, value)

  def testConstructor(self):
    return
    self.assertEqual(self.versioned._filepath, MANAGED_FILE)
    self.assertEqual(self.versioned._backup_dir, TEST_DIR)
    self.assertEqual(self.versioned._max_versions, MAX_DEPTH)
    self.assertEqual(self.versioned._undo_stack.getDepth(), 0)
    self.assertEqual(self.versioned._redo_stack.getDepth(), 0)
    self._checkState(0, [], [])

  def _checkStackState(self, file_stack, values):
    """
    Checks the values of each element in the file stack
    :param FileStack file_stack:
    :param list values:
    """
    filepaths = file_stack._getFilepaths()
    if len(filepaths) !=  len(values):
      import pdb; pdb.set_trace()
    self.assertEqual(len(filepaths), len(values))
    pairs = zip(filepaths, values)
    for filepath, value in pairs:
      self.assertTrue(checkFilepathValue(filepath, value))

  def _checkState(self, managed_file_value, undo_values, redo_values):
    self.assertTrue(
       checkFilepathValue(self.versioned._filepath, managed_file_value))
    self._checkStackState(self.versioned._undo_stack, undo_values)
    self._checkStackState(self.versioned._redo_stack, redo_values)

  def _checkpointAndUpdate(self, new_value):
    self.versioned.checkpoint()
    self._writeManagedFile(new_value)

  def testCheckpoint(self):
    return
    self._checkpointAndUpdate(1)
    self._checkState(1, [0], [])
    self._checkpointAndUpdate(2)
    self._checkpointAndUpdate(3)
    self._checkState(3, [2, 1, 0], [])

  def _testUndo(self, size):
    """
    :param int size: size of undo history
    """
    self.versioned.clear()
    self._writeManagedFile(0)
    for idx in range(1, size+1):
      self._checkpointAndUpdate(idx)
    if size == 0:
      with self.assertRaises(RuntimeError):
        self.versioned.undo()
    else:
      self.versioned.undo()
      limit = min(size, MAX_DEPTH)
      offset = max(0, size-MAX_DEPTH)
      undo_state = range(offset, limit+offset)
      undo_state.reverse()
      del undo_state[0]
      self._checkState(size-1, undo_state, [size])

  def testUndo(self):
    self._testUndo(MAX_DEPTH+1)
    self._testUndo(2)
    self._testUndo(1)
    self._testUndo(MAX_DEPTH)
    self._testUndo(0)

  def _testRedo(self, size):
    """
    :param int size: size of redo history
    """
    self.versioned.clear()
    self._writeManagedFile(0)
    for idx in range(1, size+1):
      self._checkpointAndUpdate(idx)
      self.versioned.undo()
    if size == 0:
      with self.assertRaises(RuntimeError):
        self.versioned.redo()
    else:
      self.versioned.redo()
      limit = min(size, MAX_DEPTH) + 1
      offset = max(0, size-MAX_DEPTH)
      redo_state = range(1+offset, limit+offset)
      redo_state.reverse()
      del redo_state[0]
      self._checkState(size, [0], redo_state)

  def testRedo(self):
    self._testRedo(MAX_DEPTH+1)
    self._testRedo(1)
    self._testRedo(3)
    self._testRedo(MAX_DEPTH)

  def testClear(self):
    # Populate the stacks
    self._writeManagedFile(0)
    for idx in range(1, MAX_DEPTH+1):
      self._checkpointAndUpdate(idx)
    self.versioned.undo()
    undo_state = range(MAX_DEPTH-1)
    undo_state.reverse()
    self._checkState(MAX_DEPTH-1, undo_state, [MAX_DEPTH])
    self.versioned.clear()
    self._checkState(MAX_DEPTH-1, [], [])

  def testGet(self):
    filepath = self.versioned.get()
    self.assertEqual(filepath, MANAGED_FILE)
    

if __name__ == '__main__':
    unittest.main()

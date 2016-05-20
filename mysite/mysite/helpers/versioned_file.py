"""
Creates an abstraction that allows to undo and redo versions
of a file. Core concepts:
  managed file: the file that is being versioned
  checkpoint: saved copy of the managed file
  undo: operation that reinstates the last checkpoint
  redo: operation that reinstates the last version that was
        present when an undo operation was done
"""

from file_stack import FileStack
import os


UNDO_PREFIX = "u"
REDO_PREFIX = "r"

class VersionedFile(object):

  """
  Usage example:
    versioned_file = VersionedFile(managed_file, backup_dir, max_versions)
    versioned_file.checkpoint()  # Called before an update is made
    versioned_file.undo()  # Recover a previous version
    versioned_file.checkpoint()  # Called before an update is made
    versioned_file.redo()  # Return to the version before the undo
  """

  def __init__(self, filepath, backup_dir, max_versions):
    """
    :param str filepath: File path to be managed
    :param str backup_dir:
    :param int max_versions:
    """
    self._filepath = filepath
    self._backup_dir = backup_dir
    self._max_versions = max_versions
    undo_pfx = self._filenamePrefix(UNDO_PREFIX)
    self._undo_stack = FileStack(backup_dir, undo_pfx,
        self._max_versions)
    redo_pfx = self._filenamePrefix(REDO_PREFIX)
    self._redo_stack = FileStack(backup_dir, redo_pfx,
        self._max_versions)

  def _filenamePrefix(self, pfx):
    """
    :param str pfx: prefix in the file extension
    Returns the filename prefix
    """
    full_name = os.path.split(self._filepath)[1]
    filename, ext = os.path.splitext(full_name)
    filename_pfx = "%s.%s" % (filename, pfx)
    return filename_pfx

  def checkpoint(self):
    """
    Create a checkpoint in the undo stack for the current version
    of the managed file.
    """
    self._undo_stack.push(self._filepath)

  def clear(self):
    """
    Empty the undo and redo stacks.
    """
    self._undo_stack.clear()
    self._redo_stack.clear()

  def get(self):
    """
    :returns str filepath:
    """
    return self._filepath

  def undo(self):
    """
    Reinstates the last verion of the file
    :raises RuntimeError: undo stack is empty
    """
    if self._undo_stack.isEmpty():
      raise RuntimeError("Undo stack is empty.")
    self._redo_stack.push(self._filepath)
    self._undo_stack.pop(self._filepath)
 
  def redo(self):
    """
    Undoes the last undo
    :raises RuntimeError: undo stack is empty
    """
    if self._redo_stack.isEmpty():
      raise RuntimeError("Redo stack is empty.")
    self.checkpoint()
    self._redo_stack.pop(self._filepath)

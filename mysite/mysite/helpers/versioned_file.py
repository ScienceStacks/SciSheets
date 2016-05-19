"""
Creates an abstraction that allows to undo and redo versions
of a file.
"""

from file_stack import FileStack

class VersionedFile(object):

  """
  Usage example:
    versioned_file = VersionedFile(managed_file)
    versioned_file.update()  # Called before an update is made
    versioned_file.undo()  # Recover a previous version
    versioned_file.redo()  # Undo the undo
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
    undo_pfx = self._extractFilename("u")
    self._undo_stack = FileStack(backup_dir, undo_pfx,
        self._max_versions)
    redo_pfx = self._extractFilename("r")
    self._redo_stack = FileStack(backup_dir, redo_pfx,
        self._max_versions)

  def _extractFilename(self, pfx):
    """
    :param str pfx:
    Returns the filename prefix
    """
    full_file = os.path.split(filepath)[1]
    filename, ext = os.path.splitext(full_file)
    filename_pfx = "%s.%s" % (filename, pfx)
    return filename_pfx

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
    self._undo_stack.push(self._filepath)
    self._redo_stack.pop(self._filepath)

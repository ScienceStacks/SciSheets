""" 
Presents a stack abstraction for managing a collection of files.
"""

import os
import shutil

FIRST_IDX = 1
MAX_DEPTH = 99


class FileStack(object):

  """
  Provide push, pop operations to create/access/remove files
  """

  def __init__(self, dirpath, filename_pfx, max_depth=5):
    """
    :param str dirpath: path to the directory where
                         files are stored
    :param str filename_pfx: prefix to use for saved files
    :param int max_depth: maximum number of files aved
    :raises ValueError:
    """
    self._dirpath = dirpath
    self._filename_pfx = filename_pfx
    self._max_depth = max_depth
    if max_depth > MAX_DEPTH:
      raise ValueError("max_depth == %d > %d"
          % (max_depth, MAX_DEPTH))
    if not os.path.exists(self._dirpath):
      raise ValueError("Directory %s does not exist" 
          % self._dirpath)

  def _makeFilepath(self, sfx):
    """
    Creates a filepath with the desired suffix
    :param int sfx:
    """
    if sfx < 10:
      str_sfx = "0%d" % sfx
    else:
      str_sfx = str(sfx)
    filename = "%s%s" % (self._filename_pfx, str_sfx)
    return os.path.join(self._dirpath, filename)

  def _getFilepaths(self):
     """
    Returns a list of all filepaths currently in the stack
    :return list-of-str: all filepaths used in this instance
    Notes: (1) list is ordered from top to bottom of the stack
           (2) eliminates stray history files
    """
    sfxs = range(FIRST_IDX, self._maxdepth+1)
    possible_filepaths = [self._makeFilepath(sfx) for sfx in sfxs]
    filepaths = []
    is_end = False  # Encountered end of files used
    for filepath in possible_filepaths:
      if os.path.exists(filepath):
        if is_end:
          # Eliminate old history files
          os.remove(filepath)
        else:
          filepaths.append(filepath)
      else:
        is_end_files = True
    return filepaths

  def _getTop(self):
    """
    Returns the top filepath that exists in the stack
    :returns str/None:
    """
    files = self._getFilepaths()
    if len(files) == 0:
      return None
    else:
      return files[0]

  def _adjustStack(self, is_move_down):
    """
    Copies files in the stack to adjust the stack either up or down.
    If the stack is moved up, the unused file at the end is deleted.
    :param bool is_move_down: If True, moving files down the stack
    """
    is_move_up = not is_move_down
    filepaths = self._getFilepaths()
    adj_filepaths = list(filepaths)
    if is_move_down and len(filepaths) < self._max_depth:
      new_sfx = len(filepaths) + 1
      new_filepath = self._makeFilepath(new_sfx)
      adj_filepaths.append(new_filepath)
      adj_filepaths.reverse()
      filepath_pairs = zip(filepaths[1:], filepaths[:-1])
    if is_move_up:
      adj_filepaths.reverse()
      filepath_pairs = zip(filepaths[:-1], filepaths[1:])
    # Create from/to copy pairs
    filepath_pairs = zip(filepaths[1:], filepaths[:-1])
    # Do the copies
    for from_filepath, to_filepath in filepath_pairs:
      shutils.copyfile(from_filepath, to_filepath)
    # Handle unused file in case of move up
    if is_move_up:
      last_filepath = filepaths[-1]
      os.remove(last_filepath)

  def clear(self):
    """
    Eliminates all files in the stack
    """
    for ff in self._getFilepaths():
      if os.path.exists(ff):
        os.remove(ff) 
 
  def getDepth(self):
    """
    Returns the current stack depth
    """
     
  def pop(self, to_filepath):
    """
    Copies the top of the stack to filepath 
    :param str to_filepath:
    :raises ValueError: stack is empty
    """
    from_filepath = self._getTop()
    if from_filepath is None or not os.path.exists(from_filepath):
      raise ValueError("FileStack history is empty")
    shutils.copyfile(from_filepath, to_filepath)
    self._adjustStack(is_move_down = False)
    
  def push(self, filepath):
    """
    Copies the file to the top of the stack
    :param str filepath:
    """
    to_file = self._makeFilepath(FIRST_IDX)
    self._adjustStack(is_move_down=True)
    shutils.copyfile(filepath, to_filepath)

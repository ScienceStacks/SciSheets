'''Evaluates formulas in a Table.'''

from mysite.helpers.versioned_file import VersionedFile
import cell_types
import collections
import numpy as np
import os
import pickle

THRESHOLD = 0.01  # Threshold for value comparisons

################### Classes ############################
# Used to define a DataClass
# cls is the data type that can be tested in isinstance
# cons is a function that constructs an instance of cls
#   taking as an argument a list
# Usage: data_class = DataClass(cls=np.ndarray, 
#                               cons=(lambda(x: np.array(x))))
DataClass = collections.namedtuple('DataClass', 'cls cons')

########### CONSTANTS ################
def makeArray(aList):
  return np.array(aList)
DATACLASS_ARRAY = DataClass(cls=np.ndarray,
    cons=makeArray)


################### Functions #########################
def getTableFromFile(file_path, verify=True):
  """
  Get the table from the file
  :param str table_file: full path to table file
  :param bool verify: checks the file path in the table
  :raises ValueError: Checks that the file path is set
  """
  fh = open(file_path, "rb")
  try:
    table = pickle.load(fh)  # BUG - fails here
  except Exception as e:
    import pdb; pdb.set_trace()
  fh.close()
  table.migrate()  # Handle case of older objects
  if verify and table.getFilepath() != file_path:
    raise ValueError("File path is incorrect or missing.")
  return table

def writeTableToFile(table):
  """
  Get the table from the file
  :param Table table:
  """
  # The namespace cannot be preserved in pickle since it
  # contains module objects
  table.setNamespace({})
  pickle.dump(table, open(table.getFilepath(), "wb"))
    

def getTableCopyFilepath(filename, directory):
  """
  Returns the filepath of where the table will be copied
  :param str filename: name of the file for the table w/o extension
  :return str filepath: path to the table file
  """
  full_filename = "%s.pcl" % filename
  return os.path.join(directory, full_filename)

def copyTableToFile(table, filename, directory):
  """
  Writes the table to the directory specified
  :param Table table:
  :param str filename: name of the file for the table w/o extension
  :return str filepath: path to the table file
  :sideeffect: Sets the table written to its new filepath
  """
  filepath = getTableCopyFilepath(filename, directory)
  new_table = table.copy()
  versioned_file = table.getVersionedFile()
  if versioned_file is None:
    new_table.setVersionedFile(None)
  else:
    max_versions = table.getVersionedFile().getMaxVersions()
    directory = table.getVersionedFile().getDirectory()
    new_versioned_file = VersionedFile(filepath, directory, max_versions)
    new_table.setVersionedFile(new_versioned_file)
  pickle.dump(new_table, open(filepath, "wb"))
  return filepath

def compareIterables(iter1, iter2):
  """
  Compares two iterables. Considered equal if different lengths
  but one iterable is filled with NaN or None.
  :param Iterable iter1: iterable possibly with None values
  :param Iterable iter2: iterable possibly with None values
  :return: True if equivalent; otherwise false
  """
  def sameType(val1, val2):
    """
    :param val1, val2: values to compare
    """
    types = [int, float, bool, str]
    if (val1 is None) and (val2 is None):
      return True
    elif (val1 is None) or (val2 is None):
      return False
    result = False
    for typ in types:
      if typ == float:
        if np.isnan(val1) or np.isnan(val2):
          result = np.isnan(val1) == np.isnan(val2)
          break
      if isinstance(val1, typ) and isinstance(val2, typ):
        result = True
        break
    return result
  # Make sure the inputs are iterables
  if not isinstance(iter1, collections.Iterable):
    iter1 = np.array([iter1])
  if not isinstance(iter2, collections.Iterable):
    iter2 = np.array([iter2])
  # Check the lengths, ignoring NaN and None
  if len(iter1) != len(iter2):
    min_len = min(len(iter1), len(iter2))
    max_len = max(len(iter1), len(iter2))
    if len(iter1) == max_len:
      extra_values = iter1[min_len:]
    else:
      extra_values = iter2[min_len:]
    is_okay = all([(e is None) or cell_types.isNan(e) \
        for e in extra_values])
    if not is_okay:
      return False
    length = min_len
  else:
    length = len(iter1)
  # Compare the values for the applicable lengths
  is_equal = True
  for idx in range(length):
    if not sameType(iter1[idx], iter2[idx]):
      is_equal = False
      break
    # Handle approximate equality for floats
    elif isinstance(iter1[idx], float):
      if abs(iter1[idx]) < THRESHOLD:
        denom = 1.0
      else:
        denom = iter1[idx]
      if np.isnan(iter1[idx]) != np.isnan(iter2[idx]):
        is_equal = False
        break
      if np.isnan(iter1[idx]) and np.isnan(iter2[idx]):
        break
      elif abs((iter1[idx] - iter2[idx])/denom) > THRESHOLD:
        is_equal = False
        break
    else:
      if iter1[idx] != iter2[idx]:
        is_equal = False
        break
  return is_equal

def getFileNameWithoutExtension(file_path):
  """
  Input: file_path - full path to the file
  Output: file_name - just the name, without extension
  """
  if file_path is None:
    return None
  full_file_name = os.path.split(file_path)[1]
  pos = full_file_name.index(".")
  return full_file_name[:pos]

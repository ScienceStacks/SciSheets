'''Evaluates formulas in a Table.'''

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
  if verify and table.getFilepath() != file_path:
    raise ValueError("File path is incorrect or missing.")
  return table

def writeTableToFile(table):
  """
  Get the table from the file
  :param Table table:
  """
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
  Get writes the table to the directory specified
  :param Table table:
  :param str filename: name of the file for the table w/o extension
  :return str filepath: path to the table file
  :sideeffect: Sets the table written to its new filepath
  """
  filepath = getTableCopyFilepath(filename, directory)
  new_table = table.copy()
  new_table.setFilepath(filepath)
  pickle.dump(new_table, open(filepath, "wb"))
  return filepath

def compareIterables(iter1, iter2):
  """
  Compares two iterables
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

  is_equal = True
  if not isinstance(iter1, collections.Iterable):
    iter1 = np.array([iter1])
  if not isinstance(iter2, collections.Iterable):
    iter2 = np.array([iter2])
  if len(iter1) != len(iter2):
    is_equal = False
  else:
    for idx in range(len(iter1)):
      if not sameType(iter1[idx], iter2[idx]):
        is_equal = False
        break
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

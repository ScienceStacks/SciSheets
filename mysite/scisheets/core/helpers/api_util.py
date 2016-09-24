'''Evaluates formulas in a Table.'''

from mysite.helpers.versioned_file import VersionedFile
from serialize_deserialize import serialize, deserialize
import mysite.settings as settings
import mysite.helpers.util as ut
import cell_types
from prune_nulls import pruneNulls

import collections
import numpy as np
import os
import pickle


def readObjectFromFile(filepath, verify=False):
  """
  Get the object from the file
  :param str filepath: full path to file
  :param bool verify: checks the file path if the
      object has a getFilepath method
  :return object:
  :raises ValueError: Checks that the file path is set
  Notes: Handles legacy of accessing PCL files
  """
  if ut.getFileExtension(filepath).lower() == 'pcl':
    adj_filepath = ut.changeFileExtension(filepath,
        settings.SCISHEETS_EXT)
  else:
    adj_filepath = filepath
  with open(adj_filepath, "rb") as fh:
    json_str = fh.read()
    new_object = deserialize(json_str)
  if 'getFilepath' in dir(new_object):
    if verify and new_object.getFilepath() != adj_filepath:
      if new_object.getFilepath() == filepath:
        new_object.setFilepath(adj_filepath)
      else:
        raise ValueError("File path is incorrect or missing.")
  return new_object

def writeObjectToFile(an_object, filepath=None):
  """
  Serializes and writes the object to the file
  :param object an_object:
  :param str filepath:
  :raises ValueError: if cannot find a filepath
  """
  if 'getFilepath' in dir(an_object):
    filepath = an_object.getFilepath()
  if filepath is None:
    raise ValueError("No way to find filepath")
  with open(filepath, "wb") as fh:
    fh.write(serialize(an_object))

def _serializeTable(table):
  with open(table.getFilepath(), "wb") as fh:
    fh.write(serialize(table))

def getTableCopyFilepath(filename, directory):
  """
  Returns the filepath of where the table will be copied
  :param str filename: name of the file for the table w/o extension
  :return str filepath: path to the table file
  """
  full_filename = "%s.%s" % (filename, settings.SCISHEETS_EXT)
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
  try:
    _serializeTable(new_table)
    # pickle.dump(new_table, open(filepath, "wb"))
  except Exception as e:
    import pdb; pdb.set_trace()
  return filepath

# TODO: Add test
def isEquivalentData(values1, values2):
  """
  Determines if two values are equivalent
  :param Iterable/object values1, values2:
  :return bool:
  """
  if cell_types.isStr(values1) and cell_types.isStr(values2):
    result = values1 == values2
  elif isinstance(values1, collections.Iterable)  \
      and isinstance(values2, collections.Iterable):
    result = compareIterables(values1, values2)
  elif type(values1) != type(values2):
    return False
  else:
    result = values1 == values2
  return result

def compareIterables(iter1, iter2):
  """
  Compares two iterables. Considered equal if different lengths
  but one iterable is filled with NaN or None.
  :param Iterable iter1: iterable possibly with None values
  :param Iterable iter2: iterable possibly with None values
  :return: True if equivalent; otherwise false
  """
  def makeList(val):
    result = cell_types.makeIterable(val)
    pruned_result = pruneNulls(result)
    if isinstance(pruned_result, list):
      return pruned_result
    else:
      return [v for v in pruned_result]

  # Make sure the inputs are iterables
  iter1 = makeList(iter1)
  iter2 = makeList(iter2)
  if len(iter1) != len(iter2):
    return False
  pairs = zip(iter1, iter2)
  try:
    if cell_types.isFloats(iter1):
      return all([cell_types.isEquivalentFloats(i1, i2) for i1, i2 in pairs])
  except TypeError as err:
    return False
  return all([i1 == i2 for i1, i2 in pairs])

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


def coerceValuesForColumn(column, values):
  """
  Coerces the values to the type appropriate for the column
  :param Column column:
  :return: type appropriate for column
  :raises: ValueError
  """
  data_class = column.getDataClass()
  values = data_class.cons(values)
  values.name = column.getName()
  return values

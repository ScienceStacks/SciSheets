'''
   Utilities used for testing MVCSheets code.
'''

import column as cl
import contextlib
import table as tb
import numpy as np
import os
import pickle
import StringIO
import sys


def toList(val):
  """
  Converts a value to a list.
  :param val: value to convert
  :return: list
  """
  if isinstance(val, list):
    data_list = val
  elif isinstance(val, np.ndarray):
    data_list = val.tolist()
  else:
    data_list = [val]
  return data_list

def compareValues(val1, val2):
  """
  Compares two scalars or lists
  :param val1: first value to compare
  :param val2: secondvalue to compare
  :return: Boolean
  """
  list1 = toList(val1)
  list2 = toList(val2)
  if len(list1) != len(list2):
    return False
  is_equal = True
  for idx in range(len(list1)):
    is_equal = is_equal and (list1[idx] == list2[idx])
  return is_equal

def createColumn(name, data=np.array([]), table=None, formula=None):
  """
  :param name: str column name
  :param data: np.ndarray data values
  :param table: Table that reerences the column
  :param formula: formula in column
  :return: column object with data populated
  """
  column = cl.Column(name)
  column.addCells(data)
  column.setTable(table)
  column.setFormula(formula)
  return column

def createTable(name, column_name=None):
  """
  :param name: str table name
  :param column_name: name of a column to create
  :return: Table object
  """
  table = tb.Table(name)
  if column_name is not None:
    column = cl.Column(name)
    table.addColumn(column)
  return table

@contextlib.contextmanager
def stdoutIO(stdout=None):
  """
  Captures standard output when executing a python command
  :param stdout: where standard output is directed
  """
  # Captures standard output
  # Usage: with stdoutIO() as s:
  old = sys.stdout
  if stdout is None:
    stdout = StringIO.StringIO()
  sys.stdout = stdout
  yield stdout
  sys.stdout = old


class TableFileHelper(object):
  """
  Creates and removes a dummy Table File
  """

  @classmethod
  def doesTableFileExist(cls, table_filename, filedir, suffix="pcl"):
    """
    Checks if the table file exists
    :param table_filename: table file name without extension
    :param table_filedir: directory for the table file
    :param suffix: suffix for filename
    :return: boolean
    """
    full_filename = "%s.%s" % (table_filename, suffix)
    full_path = os.path.join(filedir, full_filename)
    return os.path.exists(full_path)

  def __init__(self, table_filename, table_filedir):
    """
    :param table_filename: name of the dummy table file
    :param table_filedir: directory for the table file
    """
    self._table_filename = table_filename
    self._table_filedir = table_filedir
    self._full_path = os.path.join(table_filedir,
        "%s.pcl" % self._table_filename)

  def create(self):
    """
    Creates a Table file
    """
    if not TableFileHelper.doesTableFileExist(self._table_filename,
        self._table_filedir):
      table = tb.Table(self._table_filename)
      pickle.dump(table, open(self._full_path, "wb"))

  def destroy(self):
    """
    Destroys a Table file
    """
    if TableFileHelper.doesTableFileExist(self._table_filename,
        self._table_filedir):
      os.remove(self._full_path)

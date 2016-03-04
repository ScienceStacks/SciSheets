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


def toList(v):
  if isinstance(v, list):
    data_list = v
  elif isinstance(v, np.ndarray):
    data_list = v.tolist()
  else:
    data_list = [v]
  return data_list

def compareValues(v1, v2):
  list1 = toList(v1)
  list2 = toList(v2)
  if len(list1) != len(list2):
    return False
  r = True
  for n in range(len(list1)):
    r = r and (list1[n] == list2[n])
  return r

def createColumn(name, data=np.array([]), table=None, formula=None):
  # Returns a populated column
  column = cl.Column(name)
  column.addCells(data)
  column.setTable(table)
  column.setFormula(formula)
  return column

def createTable(name, column_name=None):
  # Returns a populated column
  table = tb.Table(name)
  if column_name is not None:
    column = cl.Column(name)
    table.addColumn(column)
  return table

@contextlib.contextmanager
def stdoutIO(stdout=None):
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
    if not TableFileHelper.doesTableFileExist(self._table_filename,
        self._table_filedir):
      table = tb.Table(self._table_filename)
      pickle.dump(table, open(self._full_path, "wb"))

  def destroy(self):
    if TableFileHelper.doesTableFileExist(self._table_filename,
        self._table_filedir):
      os.remove(self._full_path)
      self._exists = False

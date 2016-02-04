'''
   Utilities used for testing MVCSheets code.
'''

import column as cl
import contextlib
import table as tb
import numpy as np
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

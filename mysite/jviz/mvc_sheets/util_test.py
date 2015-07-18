'''
   Utilities used for testing MVCSheets code.
'''

import column as cl
import table as tb
import numpy as np


def ToList(v):
  if isinstance(v, list):
    data_list = v
  elif isinstance(v, np.ndarray):
    data_list = v.tolist()
  else:
    data_list = [v]
  return data_list

def CompareValues(v1, v2):
  list1 = ToList(v1)
  list2 = ToList(v2)
  if len(list1) != len(list2):
    return False
  r = True
  for n in range(len(list1)):
    r = r and (list1[n] == list2[n])
  return r

def CreateColumn(name, data=np.array([]), table=None, formula=None):
  # Returns a populated column
  column = cl.Column(name)
  column.AddCells(data)
  column.SetTable(table)
  column.SetFormula(formula)
  return column

def CreateTable(name, column_name=None):
  # Returns a populated column
  table = tb.Table(name)
  if column_name is not None:
    column = cl.Column(name)
    table.AddColumn(column)
  return table

'''
  Implements the column class for MVCSheets.
'''


import constants as cn
import errors as er
import numpy as np
from util import findTypeForData


class Column(object):

  def __init__(self, name, data_type=None):
    self._name = name
    self._data_type = data_type
    if self._data_type is not None:
      self._data_values = np.array([], dtype=data_type)
    else:
      self._data_values = np.array([])
    self._formula = None
    self._owning_table = None

  def _setDataType(self, data):
    # Sets the numpy data type for the data in the array
    # Input: data_list - list of data to add
    proposed_type = findTypeForData(data)
    if proposed_type is not object:
      self._data_type = proposed_type

  def addCells(self, v, replace=False):
    # Input: v - value(s) to add
    #        replace - if True, then replace existing cells
    # Refines the type to be more specific, if needed.
    # 
    if isinstance(v, list):
      new_data_list = v
    elif isinstance(v, np.ndarray):
      new_data_list = v.tolist()
    else:
      new_data_list = [v]
    # Verify the type
    self._setDataType(new_data_list)
    if replace:
      self._data_values = np.array(new_data_list, dtype=self._data_type)
    else:
      full_data_list = self._data_values.tolist()
      full_data_list.extend(new_data_list)
      self._data_values = np.array(full_data_list, dtype=self._data_type)

  def copy(self):
    # Returns a copy of this object
    result = Column(self._name, 
                    data_type = self._data_type)
    result.setFormula(self._formula)
    result.addCells(self._data_values)
    return result

  def deleteCells(self, indicies):
    # Input: indicies - list of indicies to delete
    data_list = self._data_values.tolist()
    for nn in indicies:
      del data_list[nn]
    self._data_values = np.array(data_list, dtype=object)

  def getCell(self, index):
    return self._data_values[index]

  def getCells(self):
    return self._data_values

  def getDataType(self):
    return self._data_type

  def getFormula(self):
    return self._formula

  def getName(self):
    return self._name

  def insertCell(self, val, index=None):
    # Input: val - value to insert
    #        index - where it is inserted
    #                appended to end if None
    self._setDataType([val])
    data_list = self._data_values.tolist()
    if index is None:
      index = len(self._data_values)
    data_list.insert(index, val)
    self._data_values = np.array(data_list, dtype=object)

  def numCells(self):
    return len(self._data_values)

  def rename(self, new_name):
    self._name = new_name

  # ToDo: Test
  def replaceCells(self, new_array):
    # Input: new_array - array to replace existing array
    if len(new_array) != len(self._data_values):
      raise er.InternalError("Inconsistent lengths")
    self._data_values = np.array(new_array, dtype=object)

  def setFormula(self, formula):
    # A formula is a valid python expression of a mix of numpy.array
    # scalars, and functions in math for columns that preceed
    # this column in the table.
    # Inputs: formula - valid python expression
    # Outputs: error - string giving error encountered
    try:
      _ = compile(formula, "string", "eval")  # Compilation checks syntax
      self._formula = formula
      error = None
    except Exception as e:
      error = "%s: %s" % (e[0], e[1][3])
    return error

  def setTable(self, table):
    # Sets the table being used for this column
    self._owning_table = table

  def updateCell(self, val, index):
    # Input: val - value to insert
    #        index - index of cell being updated
    #                appended to end if None
    self._setDataType([val])
    self._data_values[index] = val

'''
  Implements the column class for MVCSheets.
'''


import constants as cn
import errors as ex
import numpy as np


class Column(object):

  def __init__(self, name, data_type=None):
    self._name = name
    self._data_type = data_type
    if self._data_type is not None:
      self._data_values = np.array([], dtype=self._data_type)
    else:
      self._data_values = np.array([])
    self._formula = None
    self._owning_table = None

  def _setDataType(self, val):
    # Assigns the type setting based on the type of val,
    # assuming that there are no existing data.
    # Input: val - a value to add to the column
    if len(self._data_values) == 0 and self._data_type is None:
      if val is None:
        pass
      elif type(val) is str:
        self._data_type = object 
      elif type(val) is int:
        self._data_type = int
      elif type(val) is float:
        self._data_type = float
      else:
        raise ex.DataTypeError("%s is an unknown type" % str(val))

  def addCells(self, v, replace=False):
    # Input: v - value(s) to add
    #        replace - if True, then replace existing cells
    if isinstance(v, list):
      new_data_list = v
    elif isinstance(v, np.ndarray):
      new_data_list = v.tolist()
    else:
      new_data_list = [v]
    # Verify the type
    self._setDataType(new_data_list[0])
    if self._data_type is not None:
      for e in new_data_list:
        if e is not None and (not isinstance(e, self._data_type)):
          raise ex.DataTypeError("%g is not %s" % (e, self._data_type))
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
    self._data_values = np.array(data_list, dtype=self._data_type)

  def evaluate(self):
    # evaluates the formula, if any.
    # Replaces the data values with the formula results
    raise ex.NotYetImplemented("evaluate")

  def getCells(self):
    return self._data_values

  def getDataType(self):
    return self._data_type

  def getName(self):
    return self._name

  def insertCell(self, val, index=None):
    # Input: val - value to insert
    #        index - where it is inserted
    #                appended to end if None
    self._setDataType(val)
    data_list = self._data_values.tolist()
    if index is None:
      index = len(self._data_values)
    data_list.insert(index, val)
    self._data_values = np.array(data_list, dtype=self._data_type)

  def numCells(self):
    return len(self._data_values)

  def rename(self, new_name):
    self._name = new_name

  def setFormula(self, formula):
    # A formula is a valid python expression of a mix of numpy.array
    # scalars, and functions in math for columns that preceed
    # this column in the table.
    self._formula = formula

  def setTable(self, table):
    # Sets the table being used for this column
    self._owning_table = table

  def updateCell(self, val, index):
    # Input: val - value to insert
    #        index - index of cell being updated
    #                appended to end if None
    self._setDataType(val)
    self._data_values[index] = val

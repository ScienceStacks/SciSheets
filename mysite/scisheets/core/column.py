'''
  Implements the column class for MVCSheets.
'''


import constants as cn
import errors as ex
import numpy as np


class Column(object):

  def __init__(self, name, data_type=None):
    self._name = name
    self._data_values = np.array([])
    self._data_type = data_type
    self._formula = None
    self._owning_table = None

  def AddCells(self, v, replace=False):
    if isinstance(v, list):
      new_data_list = v
    elif isinstance(v, np.ndarray):
      new_data_list = v.tolist()
    else:
      new_data_list = [v]
    # Verify the type
    if self._data_type is not None:
      for e in new_data_list:
        if not isinstance(e, self._data_type):
          raise ex.DataTypeError("%g is not %s" % (e, self._data_type))
    if replace is False:
      full_data_list = self._data_values.tolist()
      full_data_list.extend(new_data_list)
    self._data_values = np.array(full_data_list)
    if self._owning_table is not None:
      self._owning_table.AdjustColumns()

  def Copy(self):
    # Returns a copy of this object
    result = Column(self._name, 
                    data_type = self._data_type)
    result.SetFormula(self._formula)
    result.AddCells(self._data_values)
    return result

  def DeleteCells(self, indicies=None):
    # Input: index of cells to delete (all if None)
    if indicies is None:
      self._data_values = np.empty([0])
    else:
      new_data_list = []
      for nn in range(len(self._data_values)):
        if not (nn in indicies):
          new_data_list.append(self._data_values[nn])
      self._data_values = np.array(new_data_list)
    self._owning_table.AdjustColumns()

  def Evaluate(self):
    # Evaluates the formula, if any.
    # Replaces the data values with the formula results
    raise ex.NotYetImplemented("Evaluate")

  def GetCells(self):
    return self._data_values

  def GetNumCells(self):
    return len(self._data_values)

  def GetName(self):
    return self._name

  def SetFormula(self, formula):
    # A formula is a valid python expression of a mix of numpy.array
    # scalars, and functions in math for columns that preceed
    # this column in the table.
    self._formula = formula

  def SetTable(self, table):
    # Sets the table being used for this column
    self._owning_table = table

  def UpdateCell(self, index, val):
    if index >= 0 and index < len(self._data_values):
      self._data_values[index] = val

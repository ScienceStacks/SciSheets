'''
  Implements the column class for MVCSheets.
'''


import constants as c
import exceptions as e
from numpy import array


class Column(object):

  def __init__(self, name, data_type=None)
    self._name = name
    self._data_values = array([])
    self._data_type = data_type
    self._formula = None
    self._table = None

  def AddCells(self, v, replace=False):
    if isinstance(v, list):
      new_data_list = v
    elif isinstance(v, array):
      new_data_list = v.tolist()
    else:
      new_data_list = [v]
    # Verify the type
    if self._data_type is not None:
    for e in new_data_list:
      if not isinstance(e, self._data_type):
        raise e.DataTypeError("%g is not %s" % (e, self._data_type)
    if not replace:
      full_data_list = self._data_values.tolist.extend(new_data_list)
    self._data_values = array(full_data_list)

  def Copy(self)
    # Returns a copy of this object
    result = Column(self._name, 
                    data_type = self._data_type)
    result.SetFormula(self._formula)
    result.AddCells(self._data_values)
    return result

  def DelCells(self):
    self._data_values = array([])
 
  def Evaluate(self):
    # Evaluates the formula, if any.
    # Replaces the data values with the formula results
    raise e.NotYetImplemented("Evaluate")

  def GetCells(self):
    return self._data_values

  def GetName(self):
    return self._name

  def SetFormula(self, formula):
    # A formula is a valid python expression of a mix of numpy.array
    # scalars, and functions in math for columns that preceed
    # this column in the table.
    self._formula = formula

  def SetTable(self, table):
    # Sets the table being used for this column
    self._table = table

  def UpdateCell(self, index, val):
    if index >= 0 and index < len(self._data_values):
      self._data_values[index] = val

'''
  Implements the column class for MVCSheets.
'''

from numpy import array
import constants as c

class Column(object):

  def __init__(self, name, data_type=None):
    self._name = name
    self._data_values = array([])
    self._data_type = data_type
    self._data_values = array([])
    self._formula = None

  def GetName(self):
    return self._name

  # TODO: Check type
  def UpdateCells(self, v, replace=False):
    if isinstance(v, list):
      new_data_list = v
    elif isinstance(v, array):
      new_data_list = v.tolist()
    else:
      new_data_list = [v]
    if not replace:
      full_data_list = self._data_values.tolist.extend(new_data_list)
    self._data_values = array(full_data_list)

  def DelCells(self):
    self._data_values = array([])

  def GetCells(self):
    return self._data_values

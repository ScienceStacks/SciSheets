'''
  Implements the column class
'''


import errors as er
import numpy as np
from helpers.formula_statement import FormulaStatement
from mysite.helpers.tree import Tree
from helpers.extended_array import ExtendedArray
from helpers.prune_nulls import pruneNulls
import helpers.cell_types as cell_types
import collections


class Column(Tree):
  """
  Representation of a column in a table. A column is a ctonainer
  of cells.
  """

  is_always_leaf = True  # Cannot add/modify children


  def __init__(self, 
               name, 
               data_class=cell_types.DATACLASS_ARRAY,
               asis=False):
    """
    :param str name: Name of column
    :param DataClass data_class: Class for data
    :param bool asis: opaque data if True
    """
    super(Column, self).__init__(name)
    self.setName(name)
    self.setAsis(asis)
    self._cells = []
    self._formula_statement = FormulaStatement(None, self.getName())
    self._data_class = data_class

  def getSerializationDict(self, class_variable):
    """
    Method required to serialize this class.
    :param str class_variable: key to use for class name
    :return dict:
    Notes:
    1. Does not save self._parent (in Tree). This is set by fixups
       done in deserialize().
    """
    if self.getDataClass().cls != ExtendedArray:
      raise ValueError("Only serialize ExtendedArray")
    serialization_dict = {
        class_variable: str(self.__class__),
        "_name": self.getName(),
        "_asis": self.getAsis(),
        "_cells": self.getCells(),
        "_formula": self.getFormula(),
        }
    return serialization_dict

  @classmethod
  def deserialize(cls, serialization_dict):
    """
    Creates a column object and does fixups.
    :param dict serialization_dict: created by getSerializationDict
    :return Column:
    """
    column = Column(serialization_dict["_name"])
    column.setAsis(serialization_dict["_asis"])
    column.addCells(serialization_dict["_cells"], replace=True)
    column.setFormula(serialization_dict["_formula"])
    column.setDataClass(cell_types.DATACLASS_ARRAY)
    return column

  @staticmethod
  def _adjustValue(value):
    """
    Handles the case of iterables vs. single values.
    :param value: list or iterable
    :return list: values as a list
    """
    if isinstance(value, list):
      new_data_list = value
    elif 'tolist' in dir(value):
      new_data_list = value.tolist()
    else:
      new_data_list = [value]
    return new_data_list

  def addCells(self, value, replace=False):
    """
    :param value: value(s) to add
    :param bool replace: if True, then replace existing cells
    """
    new_data_list = Column._adjustValue(value)
    # Construct the full list
    if replace:
      full_data_list = new_data_list
    else:
      full_data_list = self._cells
      full_data_list.extend(new_data_list)
    self._setDatavalues(full_data_list)

  def copy(self, instance=None):
    """
    :param Column column:
    :returns Column: copy of this object
    """
    # Create an object if one is not provided
    if instance is None:
      instance = Column(self.getName())
    # Copy properties from inherited classes
    instance = super(Column, self).copy(instance=instance)
    # Set properties specific to this class
    instance.setFormula(self.getFormula())
    instance.addCells(self.getCells())
    instance.setAsis(self.getAsis())
    instance.setDataClass(self.getDataClass())
    instance.setParent(self.getParent())
    return instance

  def deleteCells(self, indicies):
    """
    Input: indicies - list of indicies to delete
    """
    data_list = self._cells
    for index in indicies:
      del data_list[index]
    self._setDatavalues(data_list)

  def getAsis(self):
    """
    :return bool asis:
    """
    return self._asis

  def getCell(self, index):
    """
    Returns the value of a single cell
    Input: index - index of the cell to select
    """
    return self._cells[index]

  def getCells(self):
    """
    Returns the cells of the column as a numpy array
    """
    return self._cells

  def getTypeForCells(self):
    """
    :return cell_type.XType: type assigned to the column of cells
    """
    return cell_types.getIterableType(self._cells)
 

  def getDataClass(self):
    """
    Returns the class (e.g., np.array, Trinary)
    """
    return self._data_class

  def getArrayType(self):
    """
    :return: np.ndarray type if array; else, None
    """
    if (self._data_class.cls == np.ndarray)  \
        or (self._data_class.cls == ExtendedArray):
      return np.array(self._cells).dtype
    else:
      return None

  def getFormula(self):
    """
    Returns formula for the column
    """
    return self._formula_statement.getFormula()

  def getFormulaStatement(self):
    """
    Returns the formula as a python statement
    """
    return self._formula_statement.getStatement()

  def getFormulaStatementObject(self):
    """
    Returns the FormulaStatement object
    """
    return self._formula_statement

  def insertCell(self, val, index=None):
    """
    :param val: value to insert
    :param index: where it is inserted, appended to end if None
    """
    data_list = self._cells
    if index is None:
      index = len(self._cells)
    data_list.insert(index, val)
    self._setDatavalues(data_list)

  def isEquivalent(self, column):
    """
    Compares the internal state of this and the input column,
    except the owning table.
    :param Column column:
    :return bool:
    """
    if not self.getFormulaStatementObject().isEquivalent(column.getFormulaStatementObject()):
      return False
    if not self.getAsis() == column.getAsis():
      return False
    if not self.getDataClass() == column.getDataClass():
      type_list = [np.ndarray, ExtendedArray]
      is_ok = (self.getDataClass().cls in type_list)  \
         and (column.getDataClass().cls in type_list)
      if not is_ok:
        return False
    if not cell_types.isEquivalentData(self._cells, column.getCells()):
      return False
    return True

  def isExpression(self):
    return self._formula_statement.isExpression()

  def isFloats(self):
    """
    :return: True if a column of numbers
    """
    return cell_types.isFloats(self.getCells())

  def numCells(self):
    """
    Returns the number of cells in the column
    """
    return len(self._cells)

  def prunedCells(self):
    """
    Returns cells in the column, excluding ending Nulls
    """
    return pruneNulls(self._cells)

  # ToDo: Test
  def replaceCells(self, new_data):
    """
    :param new_data: array to replace existing data
    """
    if len(new_data) != len(self._cells):
      raise er.InternalError("Inconsistent lengths")
    self._setDatavalues(new_data)

  def _setDatavalues(self, values):
    """
    Sets the values for the cell
    :param values: singleton or iterable
    """
    if self._asis:
      self._cells = values
    else:
      self._cells = cell_types.coerceData(values)

  def setAsis(self, asis):
    """
    :param bool asis:
    """
    self._asis = asis

  def setDataClass(self, data_class):
    """
    Sets the class (e.g., np.array, Trinary)
    """
    self._data_class = data_class

  def setFormula(self, formula):
    """
    A formula is a valid python expression for the execution context.
    Inputs: formula - valid python expression
    Outputs: error - string giving error encountered
    """
    self._formula_statement = FormulaStatement(formula, self.getName())
    return self._formula_statement.do()

  @staticmethod
  def cleanName(name):
    """
    Removes blanks and other junk.
    :param str name:
    :return str:
    """
    return name.replace(" ", "")

  def setName(self, name):
    """
    Sets the column name
    """
    stripped_name = Column.cleanName(name)
    if Column.isPermittedName(stripped_name) is None:
      super(Column, self).setName(stripped_name)
    else:
      raise er.InternalError("%s is an invalid name" % name)

  def setTable(self, table):
    """
    Sets the table being used for this column
    """
    self.setParent(table)

  def getTable(self):
    if '_parent' not in dir(self):
      import pdb; pdb.set_trace()
    return self.getParent()

  @staticmethod
  def isPermittedName(name):
    """
    Verifies that this is a valid name for a column
    Input: name - proposed column name (str)
    Output: error - string if an error
                    None if not an error
    """
    try:
      statement = "%s = 3" % name
      _ = compile(statement, "string", "exec")
      error = None
    except SyntaxError as err:
      error = "%s produced the error: %s" % (name, str(err))
    return error

  def updateCell(self, val, index):
    """
    Input: val - value to insert
           index - index of cell being updated
                   appended to end if None
    """
    values = self._cells
    values[index] = val
    self._setDatavalues(values)

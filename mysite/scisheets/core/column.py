'''
  Implements the column class for MVCSheets.
'''


import constants as cn
import errors as er
import numpy as np
from util import findDatatypeForValues


class Column(object):

  def __init__(self, name, data_type=None):
    self._name = name
    self._datatype = data_type
    if self._datatype is not None:
      self._data_values = np.array([], dtype=data_type)
    else:
      self._data_values = np.array([])
    self._formula = None
    self._owning_table = None
    self._formula_statement = None  # Formula as a statement

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
    # Construct the full list
    if replace:
      full_data_list = new_data_list
    else:
      full_data_list = self._data_values.tolist()
      full_data_list.extend(new_data_list)
    self._datatypeFromValues(full_data_list)
    # Must update the array using the correct data type
    self._data_values = np.array(full_data_list, dtype=self._datatype)

  def copy(self):
    # Returns a copy of this object
    result = Column(self._name, 
                    data_type = self._datatype)
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
    return self._datatype

  def getFormula(self):
    return self._formula

  def getFormulaStatement(self):
    return self._formula_statement

  def getName(self):
    return self._name

  def insertCell(self, val, index=None):
    # Input: val - value to insert
    #        index - where it is inserted
    #                appended to end if None
    data_list = self._data_values.tolist()
    if index is None:
      index = len(self._data_values)
    data_list.insert(index, val)
    self._datatypeFromValues(values=data_list)
    self._data_values = np.array(data_list, dtype=self._datatype)

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

  def _datatypeFromValues(self, values=None):
    # Sets the numpy values type for the values in the array
    # Input: values - enumerable values
    #                 if None, use the columns current values
    # Sets the most specific type for the column
    if values is None:
      values = self._data_values
    self._datatype = findDatatypeForValues(values)

  def _makeStatementFromFormula(self, formula, assigned_variable):
    # TODO: Need tests
    # TODO: Improve the way that detect an expression vs. a statement
    #       so that the correct exception is returned
    # Makes the formula into a statement.
    # A formula may be an expression, one or more statements, 
    # an expression followed by one or more statements.
    # Assigns the value the _formula_statement
    # Input: formula - formula as specified
    #        assigned_variable - variable to assign if
    #                            the formula leads with an expression
    # Output: exception - exception from formula evaluation or None
    # Notes: (a) _formula_statement is changed only if formula
    #            is valid
    if formula is None:
      self._formula_statement = None
      return None
    try:
      exception_stmt = None
      _ = compile(formula, "string", "eval")
      statement = "%s = %s" % (assigned_variable, formula)
    except Exception as e:
      exception_stmt = e
    if exception_stmt is not None:
      try:
        exception_expr = None
        statement = formula
        _ = compile(statement, "string", "exec")
      except Exception as e:
        exception_expr = e
    if (exception_stmt is not None) and (exception_expr is not None):
      # Guess whether is is intended to be a statement or an expression
      # so that the correct error message can be delivered.
      try:
        pos = formula.index("=")  # See if there's an assignment
        isStmt = True
      except:
        isStmt = False
      if isStmt:
        exception = exception_stmt
      else:
        exception = exception_expr
    else:
      exception = None
    if exception is None:
      self._formula_statement = statement
    return exception

  def setFormula(self, formula):
    # A formula is a valid python expression of a mix of numpy.array
    # scalars, and functions in math for columns that preceed
    # this column in the table.
    # Inputs: formula - valid python expression
    # Outputs: error - string giving error encountered
    error = None
    exception = self._makeStatementFromFormula(formula, self.getName())
    if exception is None:
      self._formula = formula
    else:
      if isinstance(exception, tuple) and (len(exception) == 3):
        error = "%s: %s" % (e[0], e[1][3])
      else:
        error = str(exception)
    return error

  def setTable(self, table):
    # Sets the table being used for this column
    self._owning_table = table

  def updateCell(self, val, index):
    # Input: val - value to insert
    #        index - index of cell being updated
    #                appended to end if None
    values = self._data_values.tolist()
    values[index] = val
    self._datatypeFromValues(values=values)
    self._data_values = np.array(values, dtype=self._datatype)

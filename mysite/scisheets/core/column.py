'''
  Implements the column class for MVCSheets.
'''


import errors as er
import numpy as np
import util


class Column(object):
  """
  Representation of a column in a table. A column is a ctonainer
  of cells.
  """

  def __init__(self, name):
    self._name = None
    self.setName(name)
    self._data_values = np.array([])
    self._formula = None
    self._owning_table = None
    self._formula_statement = None  # Formula as a statement

  def addCells(self, value, replace=False):
    """
    Input: v - value(s) to add
           replace - if True, then replace existing cells
    Refines the type to be more specific, if needed.
    """
    if isinstance(value, list):
      new_data_list = value
    elif isinstance(value, np.ndarray):
      new_data_list = value.tolist()
    else:
      new_data_list = [value]
    # Construct the full list
    if replace:
      full_data_list = new_data_list
    else:
      full_data_list = self._data_values.tolist()
      full_data_list.extend(new_data_list)
    self._setDatavalues(full_data_list)

  def copy(self):
    """
    Returns a copy of this object
    """
    result = Column(self._name)
    result.setFormula(self._formula)
    result.addCells(self._data_values)
    return result

  def deleteCells(self, indicies):
    """
    Input: indicies - list of indicies to delete
    """
    data_list = self._data_values.tolist()
    for index in indicies:
      del data_list[index]
    self._setDatavalues(data_list)

  def getCell(self, index):
    """
    Returns the value of a single cell
    Input: index - index of the cell to select
    """
    return self._data_values[index]

  def getCells(self):
    """
    Returns the cells of the column as a numpy array
    """
    return self._data_values

  def getDataType(self):
    """
    Returns the datatype of the cell
    """
    return self._data_values.dtype

  def getFormula(self):
    """
    Returns formula for the column
    """
    return self._formula

  def getFormulaStatement(self):
    """
    Returns the formula as a python statement
    """
    return self._formula_statement

  def getName(self):
    """
    Returns the name of the column
    """
    return self._name

  def insertCell(self, val, index=None):
    """
    :param val: value to insert
    :param index: where it is inserted, appended to end if None
    """
    data_list = self._data_values.tolist()
    if index is None:
      index = len(self._data_values)
    data_list.insert(index, val)
    self._setDatavalues(data_list)

  def isFloats(self):
    """
    :return: True if a column of numbers
    """
    return util.isFloats(self.getCells())

  def numCells(self):
    """
    Returns the number of cells in the column
    """
    return len(self._data_values)

  def rename(self, new_name):
    """
    Renames the column
    """
    self.setName(new_name)

  # ToDo: Test
  def replaceCells(self, new_array):
    """
    Input: new_array - array to replace existing array
    """
    if len(new_array) != len(self._data_values):
      raise er.InternalError("Inconsistent lengths")
    self._setDatavalues(new_array)

  def _setDatavalues(self, values):
    """
    Sets the values for the cell
    :param values: singleton or iterable
    """
    self._data_values = util.makeArray(values)

  # TODO: Need tests
  # TODO: Improve the way that detect an expression vs. a statement
  #       so that the correct exception is returned
  def _makeStatementFromFormula(self, formula, assigned_variable):
    """
    Makes the formula into a statement.
    A formula may be an expression, one or more statements,
    an expression followed by one or more statements.
    Assigns the value the _formula_statement
    Input: formula - formula as specified
           assigned_variable - variable to assign if
                               the formula leads with an expression
    Output: exception - exception from formula evaluation or None
    Notes: (a) _formula_statement is changed only if formula
               is valid
    """
    if formula is None:
      self._formula_statement = None
      return None
    try:
      exception_stmt = None
      _ = compile(formula, "string", "eval")
      statement = "%s = %s" % (assigned_variable, formula)
    except SyntaxError as err:
      exception_stmt = err
    if exception_stmt is not None:
      try:
        exception_expr = None
        statement = formula
        _ = compile(statement, "string", "exec")
      except SyntaxError as err:
        exception_expr = err
    if (exception_stmt is not None) and (exception_expr is not None):
      # Guess whether is is intended to be a statement or an expression
      # so that the correct error message can be delivered.
      try:
        _ = formula.index("=")  # See if there's an assignment
        is_stmt = True
      except ValueError:
        is_stmt = False
      if is_stmt:
        exception = exception_stmt
      else:
        exception = exception_expr
    else:
      exception = None
    if exception is None:
      self._formula_statement = statement
    return exception

  def setFormula(self, formula):
    """
    A formula is a valid python expression of a mix of numpy.array
    scalars, and functions in math for columns that preceed
    this column in the table.
    Inputs: formula - valid python expression
    Outputs: error - string giving error encountered
    """
    error = None
    exception = self._makeStatementFromFormula(formula, self.getName())
    if exception is None:
      self._formula = formula
    else:
      if isinstance(exception, tuple) and (len(exception) == 3):
        error = "%s: %s" % (exception[0], exception[1][3])
      else:
        error = str(exception)
    return error

  def setName(self, name):
    """
    Sets the column name
    """
    if Column.isPermittedName(name) is None:
      self._name = name
    else:
      raise er.InternalError("%s is an invalid name" % name)

  def setTable(self, table):
    """
    Sets the table being used for this column
    """
    self._owning_table = table

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
    values = self._data_values.tolist()
    values[index] = val
    self._setDatavalues(values)

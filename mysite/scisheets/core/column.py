'''
  Implements the column class for MVCSheets.
'''


import errors as er
import numpy as np
import util.util as util
import util.api_util as api_util


########### CLASSES ##################
class Column(object):
  """
  Representation of a column in a table. A column is a ctonainer
  of cells.
  """

  def __init__(self, 
               name, 
               data_class=api_util.DATACLASS_ARRAY,
               asis=False):
    """
    :param str name: Name of column
    :param DataClass data_class: Class for data
    :param bool asis: opaque data if True
    """
    self._name = None
    self.setName(name)
    self.setAsis(asis)
    self._cells = []
    self._formula = None
    self._owning_table = None
    self._formula_statement = None  # Formula as a statement
    self._data_class = data_class

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

  def copy(self):
    """
    Returns a copy of this object
    """
    result = Column(self._name)
    result.setFormula(self._formula)
    result.addCells(self._cells)
    return result

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

  def getDataClass(self):
    """
    Returns the class (e.g., np.array, Trinary)
    """
    return self._data_class

  def getArrayType(self):
    """
    :return: np.ndarray type if array; else, None
    """
    if self._data_class.cls == np.ndarray:
      return np.array(self._cells).dtype
    else:
      return None

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
    data_list = self._cells
    if index is None:
      index = len(self._cells)
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
    return len(self._cells)

  def rename(self, new_name):
    """
    Renames the column
    """
    self.setName(new_name)

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
      self._cells = util.coerceData(values)

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
    values = self._cells
    values[index] = val
    self._setDatavalues(values)

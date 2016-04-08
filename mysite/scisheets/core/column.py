'''
  Implements the column class for MVCSheets.
'''


import errors as er
import numpy as np
import util.cell_types as cell_types
import util.api_util as api_util


########### CLASSES ##################
class FormulaStatement(object):
  """
  Creates a python statement from the formula
  Usage:
    fs = FormulaStatement(formula)
    error = fs.do()  # Constructs the statement
    statement = fs.getStatement()
  """

  def __init__(self, formula, column):
    """
    :param str formula:
    """
    self._formula = formula
    self._column = column
    self._statement = None
    self._isExpression = False
    self._isStatement = False

  def do(self):
    """
    Construct the statement
    :return str: error or None
    """
    if self._formula is None:
      self._statement = None
      self._isExpression = False
      self._isStatement = False
      return
    try:
      # See if this is an expression
      exception_stmt = None
      _ = compile(self._formula, "string", "eval")
      statement = "%s = %s" % (self._column.getName(), 
          self._formula)
      self._isExpression = True
    except SyntaxError as err:
      exception_stmt = err
    if exception_stmt is not None:
      try:
        exception_expr = None
        # See if this is a statement
        statement = self._formula
        _ = compile(statement, "string", "exec")
      except SyntaxError as err:
        exception_expr = err
    if (exception_stmt is not None) and (exception_expr is not None):
      # Guess whether is is intended to be a statement or an expression
      # so that the correct error message can be delivered.
      try:
        _ = self._formula.index("=")  # See if there's an assignment
        is_stmt = True
      except ValueError:
        is_stmt = False
      if is_stmt:
        exception = exception_stmt
      else:
        exception = exception_expr
      if isinstance(exception, tuple) and (len(exception) == 3):
        error = "%s: %s" % (exception[0], exception[1][3])
      else:
        error = str(exception)
    else:
      error = None
      self._statement = statement
    return error

  def isExpression(self):
    self.do()
    return self._isExpression

  def getFormula(self):
    return self._formula

  def getStatement(self):
    self.do()
    return self._statement


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
    self.setName(name)
    self.setAsis(asis)
    self._cells = []
    self._formula_statement = FormulaStatement(None, self)
    self._owning_table = None
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
    result.setFormula(self._formula_statement.getFormula())
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
    return self._formula_statement.getFormula()

  def getFormulaStatement(self):
    """
    Returns the formula as a python statement
    """
    return self._formula_statement.getStatement()

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
    formula_statement = FormulaStatement(formula, self)
    error = formula_statement.do()
    if error is None:
      self._formula_statement = formula_statement
    return error

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
      self._name = stripped_name
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
      import pdb; pdb.set_trace()
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

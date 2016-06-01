'''
  Implements the column class for MVCSheets.
'''

import cell_types as cell_types
import api_util as api_util
import collections


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
    exception_stmt = None
    exception_expr = None
    try:
      # See if this is an expression
      _ = compile(self._formula, "string", "eval")
      statement = "%s = %s" % (self._column.getName(), 
          self._formula)
      self._isExpression = True
      self._statement = statement
    except SyntaxError as err:
      exception_expr = err
    if exception_expr is not None:
      try:
        # See if this is a statement
        _ = compile(self._formula, "string", "exec")
        self._statement = self._formula
      except SyntaxError as err:
        exception_stmt = err
    if (exception_stmt is not None) and (exception_expr is not None):
      # Guess whether is is intended to be a statement or an expression
      # so that the correct error message can be delivered.
      if "=" in self._formula:
        exception = exception_stmt
      else:
        exception = exception_expr
      error = "%s: %s" % (exception.msg, exception.text)
    else:
      error = None
    return error

  def isExpression(self):
    self.do()
    return self._isExpression

  def getFormula(self):
    return self._formula

  def getStatement(self):
    self.do()
    return self._statement

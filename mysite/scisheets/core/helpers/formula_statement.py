'''
  Implements manager of formula statements
'''

import cell_types as cell_types
from program_executer import ProgramExecuter
import api_util as api_util
import collections
import inspect
import sys


########### CLASSES ##################
class FormulaStatement(object):
  """
  Creates a python statement from the formula
  Usage:
    fs = FormulaStatement(formula)
    error = fs.do()  # Constructs the statement
    statement = fs.getStatement()
  """

  def __init__(self, formula, name):
    """
    :param str formula:
    """
    self._formula = formula
    self._name = name
    self._statement = None
    self._isExpression = False
    self._isStatement = False

  # TODO: Getting the wrong line number
  def _exceptionLinenumber(self):
    _, _, exc_tb = sys.exc_info()
    return exc_tb.tb_lineno

  def do(self):
    """
    Construct the statement
    :return str: error or None
    """
    error = None
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
      statement = "%s = %s" % (self._name, 
          self._formula)
      self._isExpression = True
      self._statement = statement
    except SyntaxError as err:
      linenumber = 1
      error = "At line %d, %s" % (linenumber, str(err))
    if error is not None:
      executer = ProgramExecuter("formula_statement",
          self._formula, {})
      error = executer.checkSyntax()
      self._isExpression = False
      self._statement = self._formula
    return error

  def isExpression(self):
    self.do()
    return self._isExpression

  def getFormula(self):
    return self._formula

  def getStatement(self):
    self.do()
    return self._statement

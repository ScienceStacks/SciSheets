"""
This class interacts with the code generated for evaluating a
scisheet to control the execution of blocks of code. A block
of code (hereafter, just block) can be a formulas, prologue, or
epilogue.
"""

from mysite.helpers.logger import Logger
from mysite import settings
import inspect
import os
import sys

class BlockExecutionController(object):

  """
  Assists with:
    1. Controlling the execution of a code block, such as
       making exceptions precise by identifying the 
       code block and line number at which an exception occurs.
       See: startBlock, endBlock, exceptionForBlock
    2. Managing loop iterations.
       See: initializeLoop, startIteration, endIteration
  """

  def __init__(self, scisheets_api, is_logging=False, debug=False):
    """
    :param ApiFormula scisheets_api:
    :param bool is_logging: creates a log file
    """
    self.debug = debug
    self._api = scisheets_api
    self._block_linenumber = None  # Where exception occurred in block
    self._block_name = None
    self._block_start_linenumber = None  # Start of block in source
    self._caller_filename = None
    self._exception = None
    self._exception_filename = None
    if is_logging:
      self._logger = Logger(settings.SCISHEETS_LOG,
          "controller")
    else:
      self._logger = None
    self._iterations = 0
    self._is_first = True
    self._table = None
    if self._api is not None:
      self._table = self._api.getTable()

  def _log(self, name, details):
    if self._logger is not None:
      self._logger.log(name, details=details)

  # TODO: Handle different file for caller
  def startBlock(self, name):
    """
    Called at the start of a block that is being evaluated.
    :param str name: User oriented identifier of the code block
    """
    if self.debug:
      import pdb; pdb.set_trace()
    self._block_name = name
    context = inspect.getouterframes(inspect.currentframe())[1]
    linenumber = context[2]
    self._caller_filename = context[1]
    self._block_start_linenumber = linenumber + 1
    self._exception_filename = None
    self._log("start/%s" % self._block_name, "")

  def endBlock(self):
    """
    Called at the end of a block
    """
    self._log("end/%s" % self._block_name, "")
    self._block_start_linenumber = None
    self._caller_filename = None
    self._exception_filename = None
    self._block_name = None

  def exceptionForBlock(self, exception):
    """
    Called when an exception has occurred.
    :param Exception exception:
    :return str, int: block name, line number in the block
    :raises RuntimeError: if not within a block
    """
    if self._block_name is None:
      self._block_name = "Unknown"
    self._exception = exception
    _, _, exc_tb = sys.exc_info()
    self._exception_filename = exc_tb.tb_frame.f_code.co_filename
    # Check for compile error
    if 'lineno' in dir(self._exception):
      abs_linenumber = self._exception.lineno
      is_runtime_error = False
    # Must be runtime error
    else:
      abs_linenumber = exc_tb.tb_lineno
      is_runtime_error = True
    # Compute the line number of the exception
    if is_runtime_error and   \
        self._exception_filename == self._caller_filename:
      self._block_linenumber = abs_linenumber  \
          - self._block_start_linenumber + 1
    else:
      self._block_linenumber = abs_linenumber
    self._log("exception/%s" % self._block_name, self.formatError())

  def formatError(self, 
                  is_absolute_linenumber=False,
                  is_use_block_name=True):
    """
    Formats the exception to include the block and line number.
    :param bool is_absolute_linenumber: Forces message to be
                                      an absolute line number
    :param bool is_use_block_name: Use the block name in the message
    :return str/None:
    """
    if self._exception is None:
      return None
    if is_use_block_name:
      if (not is_absolute_linenumber)  \
          and self._caller_filename == self._exception_filename:
        if not "Computing" in str(self._exception):
          msg = "Computing %s near line %d: %s" % (self._block_name, 
              self._block_linenumber, str(self._exception))
        else:
          msg = str(self._exception)
      else:
        msg = "In %s near line %d: %s" % (self._exception_filename,
            self._block_linenumber, str(self._exception))
    else:
      msg = "near line %d: %s" % (self._block_linenumber, str(self._exception))
    return msg

  def initializeLoop(self):
    """
    Initializes variables before loop begins
    """
    self._iterations = 0
    self._log("initializeLoop", "")

  def startAnIteration(self):
    """
    Beginning of a loop iteration
    """
    self._iterations += 1
    self._exception = None
    for cv in self._api.getColumnVariables():
      try:
        cv.setIterationStartValue()
      except Exception as err:
        import pdb; pdb.set_trace()
        pass
    self._log("startAnIteration", "iterations=%d" % self._iterations)

  def endAnIteration(self):
    """
    End of a loop iteration
    """
    self._log("endAnIteration", "iterations=%d" % self._iterations)

  def endProgram(self, details=""):
    """
    End of a loop iteration
    """
    self._log("endProgram", details)

  def _isEquivalentValues(self):
    """
    Checks if not namespace variable has changed since the start of the iteration.
    :return bool, cv/None: True if no change; cv of first ColumnVariable that failed
    """
    for cv in self._api.getColumnVariables():
      if not cv.isNamespaceValueEquivalentToIterationStartValue():
        return False, cv
    return True, None

  def isTerminateLoop(self):
    """
    Determines if the loop should terminate
    :return bool: terminate loop if True
    """
    num_formula_columns = len(self._table.getFormulaColumns())
    outcome = ""
    done = None
    is_first = self._is_first
    if is_first:
      self._is_first = False
      done = False
      is_not_evaluate = None
      is_not_except= None
      is_equiv = None
      is_large = None
      cv_bad = None
    else:
      is_not_evaluate = not self._table.getIsEvaluateFormulas()
      is_not_except= self._exception is None
      is_equiv, cv_bad = self._isEquivalentValues()
      is_large = self._iterations >= num_formula_columns
      if is_not_evaluate:
        outcome = "True - not isEvaluateFormulas"
        done = True
      elif is_not_except and is_equiv:
        outcome = "True - not exception & equivalent values"
        done = True
      elif is_large:
        outcome = "True - iterations >= num_formula_columns"
        done = True
      else:
        outcome = "False"
        done = False
    details = "%s: not_evaluate: %s; not_except: %s;"  \
        % (outcome, is_not_evaluate, is_not_except)
    cv_msg = str(is_equiv)
    if cv_bad is not None:
        cv_msg = "%s,col=%s" % (is_equiv, cv_bad.getColumn().getName())
    details = "%s equiv: %s; first: %s; large: %s."  \
        % (details, cv_msg, is_first, is_large)
    self._log("isTerminateLoop", details)
    return done
    
  def getException(self):
    return self._exception

  def getExceptionLineNumber(self):
    return self._block_linenumber

  def setTable(self, table):
    self._table = table

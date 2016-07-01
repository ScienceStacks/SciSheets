"""
This class interacts with the code generated for evaluating a
scisheet to control the execution of blocks of code. A block
of code (hereafter, just block) can be a formulas, prologue, or
epilogue.
"""

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

  def __init__(self, scisheets_api):
    """
    :param Table table:
    """
    self._api = scisheets_api
    self._block_name = None
    self._block_start_linenumber = None  # Start of block in source
    self._block_linenumber = None  # Where exception occurred in block
    self._caller_filename = None
    self._exception = None
    self._exception_filename = None
    self._iterations = 0
    self._old_table = None
    if self._api is not None:
      self._table = self._api.getTable()
    else:
      self._table = None

  # TODO: Handle different file for caller
  def startBlock(self, name):
    """
    Called at the start of a block that is being evaluated.
    :param str name: User oriented identifier of the code block
    """
    self._block_name = name
    context = inspect.getouterframes(inspect.currentframe())[1]
    linenumber = context[2]
    self._caller_filename = context[1]
    self._block_start_linenumber = linenumber + 1
    self._exception_filename = None

  def endBlock(self):
    """
    Called at the end of a block
    """
    self._block_name = None
    self._block_start_linenumber = None
    self._caller_filename = None
    self._exception_filename = None

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
    self._old_table = None

  def startAnIteration(self):
    """
    Beginning of a loop iteration
    """
    self._exception = None
    self._old_table = self._table.copy()

  def endAnIteration(self):
    """
    End of a loop iteration
    """
    self._iterations += 1
    self._api.updateTableCellsAndColumnVariables([])

  def isTerminateLoop(self):
    """
    Determines if the loop should terminate
    :return bool: terminate loop if True
    """
    num_formula_columns = len(self._table.getFormulaColumns())
    if not self._table.getIsEvaluateFormulas():
      return True
    elif (self._exception is None)  \
        and self._table.isEquivalent(self._old_table):
      done = True
    elif self._iterations >= num_formula_columns:
       # + self._api.getDependencyCounter():
      done = True
    elif self._iterations >  \
        settings.SCISHEETS_FORMULA_EVALUATION_MAX_ITERATIONS:
      done = True
    else:
      done = False
    return done
    
  def getException(self):
    return self._exception

  def getExceptionLineNumber(self):
    return self._block_linenumber

  def setTable(self, table):
    self._table = table

"""
This class interacts with the code generated for evaluating a
scisheet to control the execution of blocks of code. A block
of code (hereafter, just block) can be a formulas, prologue, or
epilogue.
"""

from mysite import settings
import inspect
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
    self._exception = None
    self._iterations = 0
    self._old_table = None
    self._table = self._api.getTable()

  def startBlock(self, name):
    """
    Called at the start of a block that is being evaluated.
    :param str name: User oriented identifier of the code block
    """
    self._block_name = name
    context = inspect.getouterframes(inspect.currentframe())[1]
    linenumber = context[2]
    self._block_start_linenumber = linenumber + 1

  def endBlock(self):
    """
    Called at the end of a block
    """
    self._block_name = None
    self._block_start_linenumber = None


  def exceptionForBlock(self, exception):
    """
    Called when an exception has occurred.
    :param Exception exception:
    :return str, int: block name, line number in the block
    :raises RuntimeError: if not within a block
    """
    if self._block_name is None:
      raise RuntimeError ("Not in a block.")
    self._exception = exception
    _, absolute_linenumber, _ = sys.exc_info()
    # Compute the line number of the exception
    self._block_linenumber = absolute_linenumber  \
        - self._block_start_linenumber + 1

  def formatError(self):
    """
    Formats the exception to include the block and line number.
    :return str/None:
    """
    if self._exception is None:
      return None
    msg = "In %s line $%d, %s" % (self._block_name, 
        self._block_linenumber, str(self._exception))
    return msg

  def initializeLoop(self):
    """
    Initializes variables before loop begins
    """
    self._iterations = 0

  def startIteration(self):
    """
    Beginning of a loop iteration
    """
    self._exception = None
    self._old_table = self._table.copy()

  def endIteration(self):
    """
    End of a loop iteration
    """
    self._iterations += 1
    self._api.updateTableCellsAndColumnVariable([])

  def isTerminateIteration(self):
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
    elif self._iterations >= num_formula_columns  \
        + self._api.getDependencyCounter():
      done = True
    elif self._iterations >  \
        settings.SCISHEETS_FORMULA_EVALUATION_MAX_ITERATIONS
      done = True
    else:
      done = False
    return done
    
  def getException(self):
    return self._exception

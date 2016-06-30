"""
Runs a program, checking syntax. Does not depend on
the SciSheets context.
"""

from block_execution_controller import BlockExecutionController
from statement_accumulator import StatementAccumulator
import exceptions

CONTROLLER = "_program_executer_controller"


class ProgramExecuter(object):

  """
  Executes a program. Provides exception reporting.
  """

  def __init__(self, program_name, program, namespace):
    """
    :param str program_name: name of the program
    :param str program: program to execute
    :param dict namespace: Namespace in which program executes
    """
    self._program_name = program_name
    self._program = program
    self._namespace = namespace
    self._controller = BlockExecutionController(None)

  def _wrapProgram(self):
    """
    Puts a wrapper around the program so that an exception can
    be caught and its location determined within the program.
    :returns str: program wrapped in try/catch blocks
    :sideeffects: puts CONTROLLER object in the namespace
    """
    self._namespace[CONTROLLER] = self._controller
    sa = StatementAccumulator()
    sa.add("try:")
    sa.indent(1)
    statement = "%s.startBlock('%s')" % (CONTROLLER, self._program_name)
    sa.add(statement)
    sa.add(self._program)
    statement = "%s.endBlock()" % CONTROLLER
    sa.add(statement)
    sa.indent(-1)
    statement = """
except Exception as exc:
  %s.exceptionForBlock(exc)""" % CONTROLLER
    sa.add(statement)
    return sa.get()

  def checkSyntax(self, adjust_linenumber=0):
    """
    Checks the syntax.
    :param int adjust_linenumber:
    :returns str: error message or None
    """
    # Check for syntax errors
    msg = None
    lineno = None
    error = None
    try:
      exec self._program in self._namespace
    except Exception as exc:
      if isinstance(exc, exceptions.SyntaxError):
        error = exc
        lineno = exc.lineno + adjust_linenumber
    if error is not None:
      msg = "In %s, syntax error at line %d: %s" %  \
          (self._program_name, lineno, str(error))
    return msg

  def execute(self):
    """
    Executes the program.
    :returns str: error message or None
    """
    # Check for syntax errors
    wrapped_program = self._wrapProgram()
    exec wrapped_program in self._namespace
    if self.getException() is None:
      return None
    else:
      return self._controller.formatError()

  def checkSyntaxAndExecute(self, **kwargs):
    msg = self.checkSyntax(**kwargs)
    if msg is None:
      msg = self.execute()
    return msg

  def getException(self):
    return self._controller.getException()
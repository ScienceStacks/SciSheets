"""
Executes a program.
"""

from block_execution_controller import BlockExecutionController


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

  def execute(self):
    """
    Executes the program.
    """
    # pylint: disable=W0122
    try:
      self._controller.startBlock(self._program_name)
      exec self._program in self._namespace
    # pylint: disable=W0703
    except Exception as exc:
      # Report the error without changing the table
      self._controller.exceptionForBlock(exc)

  def getBlockExecutionController(self):
    return self._controller

  def formatError(self):
    return self._controller.formatError()

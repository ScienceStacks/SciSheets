"""
Runs a program created from SciSheets formulas. This creates
creating the API object and managing associated resources (e.g., table files).
"""

import api_util
from program_executer import ProgramExecuter
import os
import sys


class ProgramRunner(object):
  """
  Writes and/or runs one or more programs.
  """

  def __init__(self, 
               program, 
               table,
               user_directory=None, 
               program_filename=None):
    """
    :param str program: string of one or more python program
    :param Table table: table for which execution is done
    :param str user_directory: user directory where other
                               exported programs live
    :param str program_filename: writes file executed to this file
                             filename without extension
    """
    self._program = program
    self._table = table
    if table is None:
      raise ValueError("Must specify table.")
    self._user_directory = user_directory
    self._program_filename = program_filename
    self.writeFiles()

  def writeFiles(self, write_table=True):
    """
    Writes the program and table files.
    :param bool write_table: writes the table file if True
    :return str error: error from file I/O
    """
    full_filename = "%s.py" % self._program_filename
    program_filepath = os.path.join(self._user_directory,
        full_filename)
    try:
      with open(program_filepath, "w") as file_handle:
        file_handle.write(self._program)
    except IOError as err:
      return str(err)
    if write_table:
      api_util.copyTableToFile(self._table, 
                               self._program_filename, 
                               self._user_directory)
    return None

  def _createAPIObject(self):  
    """
    Creates the API object needed for the runtime.
    Note that the APIFormulas object is created in the program
    to avoid circular imports.
    :return str error: error from execution
    """
    namespace = self._table.getNamespace()
    namespace['_table'] = self._table
    program = """
from scisheets.core import api as api
s = api.APIFormulas(_table)
"""
    executer = ProgramExecuter("ProgramRunner._createAPIObject", program, 
        namespace)
    return executer.checkSyntaxAndExecute()

  def _executeProgram(self, program):
    """
    :param str program: program to execute
    :returns str: error from execution
    Executes as a string if there is no filepath. Otherwise,
    executes from the filepath.
    """
    error = None
    namespace = self._table.getNamespace()
    # pylint: disable=W0122
    try:
      #exec(program, globals())  # NAMESPACE
      exec program in namespace
    # pylint: disable=W0703
    except Exception as exc:
      # Report the error without changing the table
      error = exc
    if error is not None:
      msg = str(error)
    else:
      msg = None
    return msg

  def execute(self, create_API_object=False):
    """
    :param bool createAPIObject: True if the runner should create the API object
    :returns str: error from execution
    Executes as a string if there is no filepath. Otherwise,
    executes from the filepath.
    """
    executer = ProgramExecuter("ProgramRunner.execute",
        self._program, self._table.getNamespace())
    # Is this needed since I construct the correct imports?
    if not self._user_directory is None:
      sys.path.append(self._user_directory)
    if create_API_object:
      error = self._createAPIObject()
      if error is not None:
        return error
    return executer.checkSyntaxAndExecute()

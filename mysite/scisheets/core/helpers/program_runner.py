"""
Runs a program created from SciSheets formulas. This creates
creating the API object and managing associated resources (e.g., table files).
"""

from scisheets.core.helpers import api_util
from scisheets.core.helpers.program_executer import ProgramExecuter
from scisheets.core.helpers.program_generator import API_OBJECT
from mysite import settings
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
               debug=False,
               program_filename=None):
    """
    :param str program: string of one or more python program
    :param Table table: table for which execution is done
    :param str user_directory: user directory where other
                               exported programs live
    :param str program_filename: writes file executed to this file
                             filename without extension
    """
    self.debug = debug
    self._program = program
    self._table = table
    if table is None:
      raise ValueError("Must specify table.")
    self._user_directory = user_directory
    if self._user_directory is None:
      self._user_directory = settings.SCISHEETS_TEST_DIR
    self._program_filename = program_filename
    self.writeFiles()

  def writeFiles(self, write_table=True):
    """
    Writes the program and table files.
    :param bool write_table: writes the table file if True
    :return str error: error from file I/O
    """
    full_filename = "%s.py" % self._program_filename
    try:
      program_filepath = os.path.join(self._user_directory,
          full_filename)
    except Exception as err:
      import pdb; pdb.set_trace()
      pass
    try:
      with open(program_filepath, "w") as file_handle:
        file_handle.write(self._program)
    except IOError as err:
      return str(err)
    if write_table and self._table.getVersionedFile() is not None:
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
%s = api.APIFormulas(_table, is_logging=True, debug=%s)
""" % (API_OBJECT, self.debug)
    executer = ProgramExecuter("ProgramRunner._createAPIObject", program, 
        namespace)
    result = executer.execute()
    try:
      namespace[API_OBJECT] = executer.getNamespace()[API_OBJECT]
    except Exception as e:
      import pdb; pdb.set_trace()
      pass
    return result

  def execute(self, create_API_object=False):
    """
    :param bool createAPIObject: True if the runner should create the API object
    :returns str: error from execution
    Executes as a string if there is no filepath. Otherwise,
    executes from the filepath.
    """
    if create_API_object:
      error = self._createAPIObject()
      if error is not None:
        return error
    executer = ProgramExecuter(self._program_filename,
        self._program, self._table.getNamespace())
    if not self._user_directory is None:
      sys.path.append(self._user_directory)
    # Check syntax here because there may be an uncorrected
    # syntax error in a column
    msg = executer.execute()
    # Update the table columns
    namespace = executer.getNamespace()
    if API_OBJECT in namespace:
      api_object = namespace[API_OBJECT]
      api_object.updateColumnFromColumnVariables()
      api_object.controller.endProgram(
          details="After updateColumnFromColumnVariables")
    return msg

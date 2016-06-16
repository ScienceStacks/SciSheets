"""
Helper for program export and evaluation.
"""

from program_generator import API_OBJECT
import api_util
import os
import sys


class ProgramRunner(object):
  """
  Writes and/or runs one or more programs.
  Assumes that the user_directory has the file my_api.py.
  """

  def __init__(self, 
               program, 
               table=None,
               user_directory=None, 
               pgm_filename=None):
    """
    :param str program: string of one or more python program
    :param Table table: table for which execution is done
    :param str user_directory: user directory where program
                               will execute. Must have file my_api.py
    :param str pgm_filename: program filename w/o extension
    :raises: ValueError if inconsistent inputs
    """
    self._program = program
    self._table = table
    self._user_directory = user_directory
    self._pgm_filename = pgm_filename
    no_table = table is None
    no_filename = pgm_filename is None
    if (no_table and not no_filename)  \
        or (no_filename and not no_table):
      raise ValueError("A table must be specified if a pgm_filename is specified.")
    if self._pgm_filename is not None:
      self._pgm_filepath = os.path.join(self._user_directory, 
                                        "%s.py" % pgm_filename)
    else:
      self._pgm_filepath = None

  def writeFiles(self, write_table=True):
    """
    Writes the program and table files.
    :param bool write_table: writes the table file if True
    :return str error: error from file I/O
    :raises ValueError: if no valid file path
    """
    if self._pgm_filepath is None:
      raise ValueError("No file path.")
    error = None
    try:
      with open(self._pgm_filepath, "w") as file_handle:
        file_handle.write(self._program)
    except IOError as err:
      error = str(err)
    if write_table:
      api_util.copyTableToFile(self._table, 
                               self._pgm_filename, 
                               self._user_directory)
    return error

  def _createAPIObject(self):  
    """
    Creates the API object needed for the runtime.
    :return str error: error from execution
    """
    namespace = self._table.getNamespace()
    namespace['_table'] = self._table
    #globals()['_table'] = self._table  #NAMESPACE
    program = """
from scisheets.core import my_api as api
s = api.APIFormulas(_table)
"""
    error = self._executeProgram(program)
    return error

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
    if not self._user_directory is None:
      sys.path.append(self._user_directory)
    error = None
    controller = None
    if self._table is None:
      import pdb; pdb.set_trace()
    namespace = self._table.getNamespace()
    if create_API_object:
      error = self._createAPIObject()
      if error is not None:
        return error
      api_object = namespace[API_OBJECT]
      controller = api_object.controller
    if self._pgm_filepath is not None:
      self.writeFiles()
      # pylint: disable=W0122
      try:
        #execfile(self._pgm_filepath, globals())  # NAMESPACE
        execfile(self._pgm_filepath, namespace)
      # pylint: disable=W0703
      except Exception as err:
        # Report the error without changing the table
        if controller is not None:
          if controller.getException() is None:
            controller.exceptionForBlock(err, verify=False)
        error = err
    elif len(self._program) > 0:
      error = self._executeProgram(self._program)
    else:
      error = "Nothing to execute!"
    if controller is not None:
      return controller.formatError()
    else:
      return error

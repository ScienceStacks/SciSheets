"""
Helper for program export and evaluation.
"""


class ProgramRunner(object):
  """
  Writes and/or runs one or more programs.
  Assumes that the user_directory has the file my_api.py.
  """

  def __init__(self, program, user_directory=None, filename=None):
    """
    :param str program: string of one or more python program
    :param str user_directory: user directory where program
                               will execute. Must have file my_api.py
    :param str filename: filename including extension
    """
    self._program = program
    self._user_directory = user_directory
    if filename is not None:
      self._filepath = os.path.join(self._user_directory, filename)
    else:
      self._filepath = None

  def writeFile(self):
    """
    :return str error: error from file I/O
    """
    self._filepath = filepath
    error = None
    try:
      with open(self._filepath, "w") as file_handle:
        file_handle.write(self._program)
    except IOError as err:
      error = str(err)
    return error

  def _createAPIObject(self):  
    """
    Creates the API object needed for the runtime.
    :return str error: error from execution
    """
    globals()['_table'] = self._table
    program = """
import myapi as api
s = api.APIFormulas(_table)
"""
    return self._execute(program)

  def _executeProgram(self, program):
    """
    :param str program: program to execute
    :returns str: error from execution
    Executes as a string if there is no filepath. Otherwise,
    executes from the filepath.
    """
    error = None
    # pylint: disable=W0122
    try:
      exec(self._program, globals())
    # pylint: disable=W0703
    except Exception as err:
      # Report the error without changing the table
      error = err
    if error is not None:
      # TODO: Better error message
      #msg = "%s: %s" % (error.msg, error.text)
      msg = str(error)
    else:
      msg = None
    return msg

  def execute(self, createAPIObject=False):
    """
    :param bool createAPIObject: True if the runner creates the API object
    :returns str: error from execution
    Executes as a string if there is no filepath. Otherwise,
    executes from the filepath.
    """
    if not self._user_directory is None:
      sys.path.append(self._user_directory)
    error = None
    if createAPIObject:
      error = self._createAPIObject()
    if error is None:
      if self._filepath is not None:
        # pylint: disable=W0122
        try:
          execfile(self._filepath, globals())
        # pylint: disable=W0703
        except Exception as err:
          # Report the error without changing the table
          error = err
      elif len(self._program) > 0:
        error = self._executeProgram(self._program)
    if error is not None:
      return str(error)
    else:
      return msg

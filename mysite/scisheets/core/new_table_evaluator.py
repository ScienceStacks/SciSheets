"""
Compiles Python statements to evaluates formulas in a Table.
Sets up the runtime environment.
  1. Write updated table to appropriate destination
  2. Create the API object for the script
Runs the compiled statements.
"""

import helpers.api_util as api_util
from helpers.program_generator import API_OBJECT, ProgramGenerator
import sys
import os
import numpy as np



######################## CLASSES ####################
class TableEvaluator(object):
  """
  Controls statement generation and sets up runtime, as required.
  """

  def __init__(self, table):
    # Inputs: table - table to evaluate
    self._table = table

  def evaluate(self, user_directory=None):
    """
    Evaluates the formulas in a Table and assigns the results
    :param user_directory: path to user exported codes
    :param table_filepath: path to table file
    :return: errors from execution or None
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterate N (#formulas) times to handle dependencies
               between formulas
    """
    if user_directory is None:
      user_directory = os.path.dirname(__file__)
    pg = ProgramGenerator(self, user_directory)
    program = pg.makeScriptProgram()
    # Create the execution environment for the compiled statements
    globals()['_table'] = self._table
    statement = """
import api
s = api.APIFormulas(_table)
"""
    envir_sr = StatementRunner(statement)
    error = envir_sr.execute()
    if error is not None:
      return error
    # Run the statements from a file
    sys.path.append(user_directory)
    sr = StatementRunner(program)
    file_path = os.path.join(user_directory, GENERATED_FILE)
    sr.writeFile(file_path)
    return sr.execute()

  # pylint: disable=R0913
  # pylint: disable=R0914
  # pylint: disable=R0915
  def export(self,
             function_name=None,
             inputs=None,
             outputs=None,
             user_directory=None,
             py_file_path=None)
    """
    Exports the table as python code
    :param function_name: string name of the function to be created
    :param inputs: list of column names that are input to the function
    :param outputs: list of columns that are output from the function
    :param user_directory: directory where user functions are located
    :param py_file_path: full path to the python file to be written
    :return: error - string from the file export
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterates N (#formulas) times to handle dependencies
               between formulas
    """
    # Initializations
    if inputs is None:
      inputs = []
    if outputs is None:
      outputs = []
    if function_name is None:
      function_name = DEFAULT_FUNCTION_NAME
    if py_file_path is None:
      py_file_path = os.path.join(user_directory, file_name)
    # Construct the function program
    pg = ProgramGenerator(self, user_directory)
    function_program = pg.makeFunction(function_name, inputs, outputs)
    # Write the function file
    file_name = "%s.py" % function_name
    sr = StatementRunner(sa.get())
    error = sr.writeFile(py_file_path)
    if error is not None:
      return "Error constructing %s: %s" % (py_file_path, error)
    # Create the test file
    test_program = pg.makeTestProgram(function_name, inputs, outputs)
    test_sr = StatementRunner(test_program)
    test_file_name = "test_%s" % file_name
    test_file_path = os.path.join(user_directory, test_file_name)
    error = test_sr.writeFile(test_file_path)
    if error is not None:
      return "Error constructing %s: %s" % (test_file_path, error)
    return None


class StatementRunner(object):
  """
  Runs one or more statements
  This must be in the same file as the caller because of the way
  python manages globals.
  """

  def __init__(self, statement):
    """
    :param str statement: string of one or more python statement
    """
    self._statement = statement
    self._filepath = None

  def writeFile(self, filepath):
    """
    :param str filepath: where statement are written
    :return str error: error from file I/O
    """
    self._filepath = filepath
    error = None
    try:
      with open(self._filepath, "w") as file_handle:
        file_handle.write(self._statement)
    except IOError as err:
      error = str(err)
    return error

  def execute(self):
    """
    :returns str: error from execution
    Executes as a string if there is no filepath. Otherwise,
    executes from the filepath.
    """
    error = None
    if self._filepath is not None:
      # pylint: disable=W0122
      try:
        execfile(self._filepath, globals())
      # pylint: disable=W0703
      except Exception as err:
        # Report the error without changing the table
        error = err
    elif len(self._statement) > 0:
      # pylint: disable=W0122
      try:
        exec(self._statement, globals())
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

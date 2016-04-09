"""
Compiles Python statements to evaluates formulas in a Table.
Sets up the runtime environment.
Runs the compiled statements.
"""

import util.api_util as api_util
from util.statement_manager import StatementAccumulator
import sys
import os
import numpy as np

GENERATED_FILE = "_generated.py"
DEFAULT_FUNCTION_NAME = "MyFunction"
IGNORE_PREFIX = ['main_', 'test_', '__']
PY_SUFFIX = ".py"
API_OBJECT = "s"



######################## CLASSES ####################
class TableEvaluator(object):
  """
  Evaluates and otherwise processes formulas in a table.
  Two kinds of files are generated:
    a) Formula execution files. For table evaluation,
       this is a script. For table export, this is a function.
    b) Unittest file for table export.
  Formula execution files are structured into sections. For
  table evaluation this consists of:
    1. Prologue statements: executed first and only once.
       Note that the APIFormulas object is created by the
       script runner.
    2. Variable assignment statements that assign column values
       to variables used in the script.
    3. Formula evaluation blocks, one for each formula.
    4. Column value assignment statements that assign script
       variables to their associated column values.
  Exported functions have the following structure:
    1. Prologue statements. This includes the creation of the
       Plugin API object.
    2. Function header (def statement)
    3. Variable assignment statements (but not for the 
       function inputs).
    4. Return statement
  In addition a test file is created that calls the exported function
  and verifies that the function produces the output columns in
  the table when it is called with the input columns.
  Code generated for these blocks often makes use of the
  api object. For table evaluation, this has the class APIFormulas.
  For exported functions, this has the class APIPlugin.
  """

  def __init__(self, table):
    # Inputs: table - table to evaluate
    self._table = table
    # True if have written function that converts an array
    self._created_convert_to_array = False

  @staticmethod
  def _findFilenames(dir_path, suffix=PY_SUFFIX):
    """
    :param dir_path: directory path to search
    :param suffix: suffix to select
    :return: list of names of file names that have suffix (w/o suffix)
    """
    selected_filenames = []
    files = [f for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))   \
           and f[-len(suffix):] == suffix]
    for name in files:
      is_valid_file = np.array([name.find(p, 0, len(p)) == -1
                    for p in IGNORE_PREFIX]).all()
      if is_valid_file:
        new_name = name[:len(name)-len(suffix)]
        selected_filenames.append(new_name)
    return selected_filenames

  def getTable(self):
    """
    :return: table for the TableEvaluator
    """
    return self._table

  @staticmethod
  #TODO: More robust approach to finding implied imports
  def _makeFormulaImportStatements(user_directory, formula_columns):
    """
    Construct import statements for the imports implied by the
    functions used in a formula. The approach taken isn't
    very robust:
      1. Find all .py files in the user's python directory. The
         function name should be the same as the file name.
      2. If a formula contains the file name (function name), then
         an import is generated.
    :param user_directory: directory to search for user python files
    :param formula_columns: list of columns that have a formula
    :return: list of import statements for files in the user directory
    A side effect is that the python path is changed.
    """
    formulas = [fc.getFormula() for fc in formula_columns]
    python_filenames = TableEvaluator._findFilenames(user_directory)
    # Determine which files are referenced in a formula
    referenced_filenames = []
    for name in python_filenames:
      for formula in formulas:
        if name in formula:
          referenced_filenames.append(name)
          break
    # Construct the import statements
    statements = []
    for name in referenced_filenames:
      statement = "from %s import %s" % (name, name)
      statements.append(statement)
    # Update the python path to find the imports
    sys.path.append(user_directory)
    return statements

  def _getSelectedColumns(self, excludes=None, only_includes=None):
    """
    Finds the columns matching the specified criteria.
    :param list-of-str excludes: list of column names not to be initialized
    :param list-of-str only_includes: list of the column names to be initialized
    :return list-of-Column: columns selected
    Notes: if excludes and only_includes are None, then all columns
    are initialized
    """
    if only_includes is None:
      columns = self._table.getColumns()
    else:
      columns = []
      for name in only_includes:
        columns.append(self._table.columnFromName(name))
    if excludes is None:
      excludes = []
    return [c for c in columns if c.getName() not in excludes]

  def _makeVariableAssignmentStatements(self, prefix="", **kwargs):
    """
    Creates statements that assign column values to variables.
    :param str prefix: prefix to construct full API object
    """
    statements = ["# Assign column values to program variables."]
    full_object = "%s%s" % (prefix, API_OBJECT)
    columns = self._getSelectedColumns(**kwargs)
    for column in columns:
      name = column.getName()
      statement = "%s = %s.getColumnValues('%s')" %   \
          (name, full_object, name)
      statements.append(statement)
    return statements

  def _makeColumnValuesAssignmentStatements(self, **kwargs):
    """
    Creates statements that assign column values to variables.
    Note that the assumption is that the variable name is the same
    as the column name
    """
    statements = ["", "# Assign program variables to columns values."]
    columns = self._getSelectedColumns(**kwargs)
    for column in columns:
      name = column.getName()
      statement = "%s.setColumnValues('%s', %s)" % (API_OBJECT, name, name)
      statements.append(statement)
    return statements

  def _formulaColumns(self, exclude="!_%$#"):
    """
    :param exclude: string that, if present, excludes formula
                    the default value should never appear
    :return: list of columns that have a formula
    """
    return [fc for fc in self._table.getColumns()
            if fc.getFormula() is not None
              and exclude not in fc.getFormula()]

  def _makePrologueStatements(self, user_directory=None):
    """
    Creates the imports that go at the head of the file
    :param user_directory: directory where user functions are located
    :return: list of statements constructed
    """
    # Initializations
    sa = StatementAccumulator(['prolog'])
    formula_columns = self._formulaColumns()
    # Construct the imports
    statement = '''import my_api as api
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp
from sympy import *
from numpy import nan  # Must follow sympy import '''
    sa.add(statement)
    if user_directory is not None:
      statement =  \
          TableEvaluator._makeFormulaImportStatements(user_directory,
                                                      formula_columns)
    sa.add(statement)
    return [sa.get()]

  # pylint: disable=R0913
  # pylint: disable=R0914
  # pylint: disable=R0915
  def _makeFormulaStatements(self):
    """
    Constructs a script to evaluate table formulas.
    :return: list of statements constructed
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterate N (#formulas) times to handle dependencies
               between formulas
    """
    # Initializations
    sa = StatementAccumulator(['formulas'])
    formula_columns = self._formulaColumns()
    num_formulas = len(formula_columns)
    if num_formulas == 0:
      return []
    # Statements that evaluate the formulas
    sa.add("# Evaluate the formulas.")
    # Special case for a single formula column
    if num_formulas == 1:
      column = formula_columns[0]
      sa.add(column.getFormulaStatement())
    else:
      sa.add("for nn in range(%d):" % num_formulas)
      sa.indent(1)
      for column in formula_columns:
        sa.add("try:")
        sa.indent(1)
        sa.add(column.getFormulaStatement())
        name = column.getName()
        if column.isExpression():
          sa.add("%s = %s.coerceValues('%s', %s)"  \
              % (name, API_OBJECT, name, name))
        sa.indent(-1)
        sa.add("except Exception as e:")
        sa.indent(1)
        sa.add("if nn == %d:" % (num_formulas-1))
        sa.indent(1)
        sa.add("raise Exception(e)")
        sa.add("break")
        sa.indent(-2)
    return [sa.get()]

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
    sa = StatementAccumulator(["generated", "script"])
    if user_directory is None:
      user_directory = os.path.dirname(__file__)
    # File Prologue
    statement = '''# Evaluation of the table %s.

    ''' % self._table.getName()
    sa.add(statement)
    sa.add(self._makePrologueStatements(
        user_directory=user_directory))
    statement = """
# Uncomment the following to execute standalone
#_table = api.getTableFromFile('%s')
#%s = api.APIFormulas(_table) 
""" % (self._table.getFilepath(), API_OBJECT) 
    sa.add(statement)
    # Assign the column values to script variables
    sa.add(self._makeVariableAssignmentStatements())
    # Create the formula evaluation blocks
    sa.add(self._makeFormulaStatements())
    # Assign script variable to the column values
    sa.add(self._makeColumnValuesAssignmentStatements())
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
    sr = StatementRunner(sa.get(name="generated"))
    file_path = os.path.join(user_directory, GENERATED_FILE)
    sr.writeFile(file_path)
    return sr.execute()

  def _makeAPIPluginInitializationStatements(self, function_name, prefix=""):
    """
    :param function_name: string name of the function to be created
    :param str prefix: prefix for API Object
    """
    full_object = "%s%s" % (prefix, API_OBJECT)
    table_filepath = self._table.getFilepath()
    statement = """%s = api.APIPlugin('%s')
%s.initialize()""" % (full_object, table_filepath, full_object)
    return statement

  # pylint: disable=R0913
  # pylint: disable=R0914
  # pylint: disable=R0915
  def export(self,
             function_name=None,
             inputs=None,
             outputs=None,
             py_file_path=None,
             table_filename=None,
             user_directory=None):
    """
    Exports the table as python code
    :param function_name: string name of the function to be created
    :param inputs: list of column names that are input to the function
    :param outputs: list of columns that are output from the function
    :param py_file_path: full path to the python file to be written
    :param table_filename: name of the table file
    :param user_directory: directory where user functions are located
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
    file_name = "%s.py" % function_name
    sa = StatementAccumulator(["export"])
    # File Prologue
    statement = '''# Export of the table %s

    ''' % self._table.getName()
    sa.add(statement)
    sa.add(self._makePrologueStatements(
        user_directory=user_directory))
    sa.add("")
    # Create the API object
    api_util.writeTableToFile(self._table)  # Update the table
    statement = self._makeAPIPluginInitializationStatements(function_name)
    sa.add(statement)
    # Make the function definition
    sa.add(TableEvaluator._makeFunctionStatement(function_name, 
        inputs))
    sa.indent(1)
    # Assign the column values to function variables.
    # Note that inputs and outputs are not assigned.
    excludes = list(inputs)
    excludes.extend(outputs)
    sa.add(self._makeVariableAssignmentStatements(excludes=excludes))
    # Create the formula evaluation blocks
    sa.add(self._makeFormulaStatements())
    # Make the return statement
    sa.add(TableEvaluator._makeReturnStatement(outputs))
    # Write the main file
    if py_file_path is None:
      py_file_path = os.path.join(user_directory, file_name)
    sr = StatementRunner(sa.get())
    error = sr.writeFile(py_file_path)
    if error is not None:
      return "Error constructing %s: %s" % (py_file_path, error)
    # Create the test file
    test_statements = self._makeTestStatements(function_name, inputs, outputs)
    test_sr = StatementRunner(test_statements)
    test_file_name = "test_%s" % file_name
    test_file_path = os.path.join(user_directory, test_file_name)
    error = test_sr.writeFile(test_file_path)
    if error is not None:
      return "Error constructing %s: %s" % (test_file_path, error)
    return None

  @staticmethod
  def _makeOutputStr(outputs):
    """
    :param outputs: list of columns that are output from the function
    :return: statement
    """
    return ",".join(outputs)

  def _makeTestStatements(self, function_name, inputs, outputs):
    """
    Creates contents of a separate test file
    :param function_name: string name of the function to be created
    :param inputs: list of column names that are input to the function
    :param outputs: list of columns that are output from the function
    :return str: statements for test file
    """
    sa = StatementAccumulator(["tests"])
    prefix = "self."
    output_str = TableEvaluator._makeOutputStr(outputs)
    statement = '''"""
Tests for %s
"""

import my_api as api
from %s import %s
import unittest


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class Test%s(unittest.TestCase):
''' % (function_name, function_name, function_name, function_name)
    sa.add(statement)
    # Construct setup method
    sa.indent(1)
    sa.add("def setUp(self):")
    sa.indent(1)
    statement = self._makeAPIPluginInitializationStatements(
        function_name, prefix=prefix)
    sa.add(statement)
    sa.indent(-1)
    # Construct the test function header
    sa.add("def testBasics(self):")
    sa.indent(1)
    # Assign values to the columns
    sa.add(self._makeVariableAssignmentStatements( \
        prefix=prefix, only_includes=inputs))
    # Construct the call to the function being tested
    statement =  TableEvaluator._makeOutputStr(outputs)
    statement += " = %s(" % function_name
    statement += ",".join(inputs)
    statement += ")"
    sa.add(statement)
    # Construct the tests
    for column_name in outputs:
      statement = "self.assertTrue(self.%s.compareToColumnValues('%s', %s))"  \
          % (API_OBJECT, column_name, column_name)
      sa.add(statement)
    sa.indent(-2)
    # Write the epilogue
    statement = """

if __name__ == '__main__':
  unittest.main()"""
    sa.add(statement)
    return sa.get()

  @staticmethod
  def _makeReturnStatement(outputs):
    """
    :param outputs: list of columns that are output from the function
    :return: statements
    """
    return "\nreturn %s" % TableEvaluator._makeOutputStr(outputs)

  @staticmethod
  def _makeFunctionStatement(function_name, inputs):
    """
    :param function_name: string name of the function to be created
    :param inputs: list of column names that are input to the function
    :return: statements
    """
    statement = "def %s(" % function_name
    statement += ",".join(inputs)
    statement += "):"
    return statement


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

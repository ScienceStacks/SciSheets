"""
Compiles Python statements to evaluates formulas in a Table.
Sets up the runtime environment.
Runs the compiled statements.
"""

import util.api_util as api_util
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
    1. Prolog statements: executed first and only once.
       Note that the APIFormulas object is created by the
       script runner.
    2. Variable assignment statements that assign column values
       to variables used in the script.
    3. Formula evaluation blocks, one for each formula.
    4. Column value assignment statements that assign script
       variables to their associated column values.
  Exported functions have the following structure:
    1. Prolog statements. This includes the creation of the
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

  def _makePrologStatements(self, user_directory=None):
    """
    Creates the imports that go at the head of the file
    :param user_directory: directory where user functions are located
    :return: list of statements constructed
    """
    # Initializations
    indent = 0
    statements = []  # List of statements in the file
    formula_columns = self._formulaColumns()
    # Construct the imports
    import_statements = ['''import my_api as api
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp
from sympy import *
from numpy import nan  # Must follow sympy import ''']
    if user_directory is not None:
      import_statements.extend(
          TableEvaluator._makeFormulaImportStatements(user_directory,
                                                      formula_columns))
    statements.extend(TableEvaluator._indent(import_statements, indent))
    return statements

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
    indent = 0
    statements = []  # List of statements in the file
    formula_columns = self._formulaColumns()
    num_formulas = len(formula_columns)
    if num_formulas == 0:
      return statements
    # Statements that evaluate the formulas
    statement = "# Evaluate the formulas."
    statements.extend(TableEvaluator._indent(["", statement], indent))
    # Special case for a single formula column
    if num_formulas == 1:
      column = formula_columns[0]
      statements.extend(TableEvaluator._indent(
          [column.getFormulaStatement()], indent))
    else:
      statement = "for nn in range(%d):" % num_formulas
      statements.extend(TableEvaluator._indent([statement], indent))
      indent += 1
      for column in formula_columns:
        statement = "try:"
        statements.extend(TableEvaluator._indent([statement], indent))
        indent += 1
        statements.extend(TableEvaluator._indent(
            [column.getFormulaStatement()], indent))
        name = column.getName()
        if column.isExpression():
          statement = "%s = %s.coerceValues('%s', %s)"  \
              % (name, API_OBJECT, name, name)
          statements.extend(TableEvaluator._indent([statement], indent))
        indent -= 1
        statement = "except Exception as e:"
        statements.extend(TableEvaluator._indent([statement], indent))
        indent += 1
        statement = "if nn == %d:" % (num_formulas-1)
        statements.extend(TableEvaluator._indent([statement], indent))
        indent += 1
        statement = "raise Exception(e)"
        statements.extend(TableEvaluator._indent([statement], indent))
        statement = "break"
        statements.extend(TableEvaluator._indent([statement], indent))
        indent -= 2
    return statements

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
    indent = 0
    if user_directory is None:
      user_directory = os.path.dirname(__file__)
    # File Prolog
    header_comments = '''# Evaluation of the table %s.

    ''' % self._table.getName()
    statements = [header_comments]
    statements.extend(TableEvaluator._indent(
        self._makePrologStatements(user_directory=user_directory),
        indent))
    statement = """
# Uncomment the following to execute standalone
#_table = api.getTableFromFile('%s')
#%s = api.APIFormulas(_table) 
""" % (self._table.getFilepath(), API_OBJECT) 
    statements.extend(TableEvaluator._indent([statement], indent))
    # Assign the column values to script variables
    statements.extend(TableEvaluator._indent(  \
        self._makeVariableAssignmentStatements(), indent))
    # Create the formula evaluation blocks
    statements.extend(TableEvaluator._indent(  \
        self._makeFormulaStatements(), indent))
    # Assign script variable to the column values
    statements.extend(TableEvaluator._indent(  \
        self._makeColumnValuesAssignmentStatements(), indent))
    # Write the statements to execute
    file_path = os.path.join(user_directory, GENERATED_FILE)
    TableEvaluator._writeStatementsToFile(statements, file_path)
    # Create the execution environment for the compiled statements
    globals()['_table'] = self._table
    statement = """
import api
s = api.APIFormulas(_table)
"""
    error = TableEvaluator._executeStatements(statement)
    if error is not None:
      return error
    # Execute the compiled statements
    statements = open(file_path).read()
    error = TableEvaluator._executeStatements(statements)
    if error is not None:
      return error
    return None


  @staticmethod
  def _indent(statements, indent_level):
    """
    :param statements: list of statements
    :param indent_level: integer level of indentation
    :return: list of indented statements
    """
    indents = " " * 2*indent_level
    result = []
    for statement in statements:
      new_statement = statement.replace("\n", "\n" + indents)
      result.append("%s%s" % (indents, new_statement))
    return result

  def _makeAPIPluginInitializationStatements(self, function_name, prefix=""):
    """
    :param function_name: string name of the function to be created
    :param str prefix: prefix for API Object
    """
    full_object = "%s%s" % (prefix, API_OBJECT)
    table_filepath = self._table.getFilepath()
    statement = """
%s = api.APIPlugin('%s')
%s.initialize()
""" % (full_object, table_filepath, full_object)
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
    indent = 0
    # File Prolog
    header_comments = '''# Export of the table %s

    ''' % self._table.getName()
    statements = [header_comments]
    statements.extend(TableEvaluator._indent(
        self._makePrologStatements(user_directory=user_directory),
        indent))
    # Create the API object
    api_util.writeTableToFile(self._table)  # Update the table
    statement = self._makeAPIPluginInitializationStatements(function_name)
    statements.extend(TableEvaluator._indent([statement], indent))
    # Make the function definition
    statements.extend(TableEvaluator._indent(
        [TableEvaluator._makeFunctionStatement(function_name, inputs)],
        indent))
    indent += 1
    # Assign the column values to function variables.
    # Note that inputs and outputs are not assigned.
    excludes = list(inputs)
    excludes.extend(outputs)
    statements.extend(TableEvaluator._indent(  \
        self._makeVariableAssignmentStatements(excludes=excludes), indent))
    # Create the formula execution blocks
    statements.extend(TableEvaluator._indent(self._makeFormulaStatements(), 
        indent))
    # Make the return statement
    statement = TableEvaluator._makeReturnStatement(outputs)
    statements.extend(TableEvaluator._indent([statement], indent))
    # Write the main file
    if py_file_path is None:
      py_file_path = os.path.join(user_directory, file_name)
    error = TableEvaluator._writeStatementsToFile(statements, py_file_path)
    if error is not None:
      return "Error constructing %s: %s" % (py_file_path, error)
    # Create the test file
    test_statements = self._makeTestStatements(function_name, inputs, outputs)
    test_file_name = "test_%s" % file_name
    test_file_path = os.path.join(user_directory, test_file_name)
    error = TableEvaluator._writeStatementsToFile(test_statements, test_file_path)
    if error is not None:
      return "Error constructing %s: %s" % (test_file_path, error)
    return None

  @staticmethod
  def _writeStatementsToFile(statements, file_path):
    """
    Writes the list of statements to the file
    :param statements: list of statements
    :param file_path: path to file
    :return: error from IO
    """
    try:
      with open(file_path, "w") as file_handle:
        file_handle.writelines(["%s\n" % s for s in statements])
      error = None
    except IOError as err:
      error = str(err)
    return error

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
    :return: statements
    """
    indent = 0
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
    statements = [statement]
    # Construct setup method
    indent += 1
    statement = "def setUp(self):"
    statements.extend(TableEvaluator._indent([statement], indent))
    indent += 1
    statement = self._makeAPIPluginInitializationStatements(function_name, 
        prefix=prefix)
    statements.extend(TableEvaluator._indent([statement, ""], indent))
    indent -= 1
    # Construct the test function header
    statement = "def testBasics(self):"
    statements.extend(TableEvaluator._indent([statement], indent))
    indent += 1
    # Assign values to the columns
    statements.extend(TableEvaluator._indent(  \
        self._makeVariableAssignmentStatements( \
        prefix=prefix, only_includes=inputs), indent))
    # Construct the call to the function being tested
    statement =  TableEvaluator._makeOutputStr(outputs)
    statement += " = %s(" % function_name
    statement += ",".join(inputs)
    statement += ")"
    statements.extend(TableEvaluator._indent([statement, ""], indent))
    # Construct the tests
    for column_name in outputs:
      statement = "self.assertTrue(self.%s.compareToColumnValues('%s', %s))"  \
          % (API_OBJECT, column_name, column_name)
      statements.extend(TableEvaluator._indent([statement], indent))
    return statements

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

  @staticmethod
  def _executeStatements(statements):
    """
    Executes one or more statements contained in a string
    :param statements: string or list of str  of one or 
                       more python statements
    :return: str error from the execution or None
    :raises: ValueError if invalid input
    """
    if isinstance(statements, list):
      statements = '\n'.join(statements)
    elif isinstance(statements, str):
      statements = statements
    else:
      raise ValueError("Must be a str or list.")
    # pylint: disable=W0122
    try:
      exec(statements, globals())
      error = None
    # pylint: disable=W0703
    except Exception as err:
      # Report the error without changing the table
      error = str(err)
    return error

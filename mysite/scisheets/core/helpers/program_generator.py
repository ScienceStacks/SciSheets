"""
Compiles Python statements that evaluate formulas in a Table.
"""

import api_util
from statement_accumulator import StatementAccumulator
from mysite.settings import SCISHEETS_PLUGIN_PYDIR,  \
    SCISHEETS_PLUGIN_PYPATH
import os
import numpy as np

DEFAULT_FUNCTION_NAME = "MyFunction"
IGNORE_PREFIX = ['main_', 'test_', '__']
PY_SUFFIX = ".py"
API_OBJECT = "s"



################## INTERNAL FUNCTIONS#################
def _makeOutputStr(outputs):
  """
  :param outputs: list of columns that are output from the function
  :return: statement
  """
  return ",".join(outputs)

def _makeReturnStatement(outputs):
  """
  :param outputs: list of columns that are output from the function
  :return: statements
  """
  return "\nreturn %s" % _makeOutputStr(outputs)

def _makeFunctionStatement(function_name, inputs):
  """
  :param function_name: string name of the function to be created
  :param inputs: list of column names that are input to the function
  :return: statements
  """
  statement = "def %s(" % function_name
  statement += ", ".join(inputs)
  statement += "):"
  return statement


######################## CLASSES ####################
class ProgramGenerator(object):
  """
  Evaluates and otherwise processes formulas in a table.
  Returns a program as a string.
  The following programs are created.
    a) Formula execution program. For table evaluation,
       this is a script. For table export, this is a function.
    b) Unittest program for table export.
  Formula execution programs are structured into sections. For
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
  In addition, a test program is created that calls the exported function
  and verifies that the function produces the output columns in
  the table when it is called with the input columns.
  Code generated for these blocks often makes use of the
  api object. For table evaluation, this has the class APIFormulas.
  For exported functions, this has the class APIPlugin.
  """

  def __init__(self, 
               table, 
               user_directory, 
               plugin_directory=SCISHEETS_PLUGIN_PYDIR,
               plugin_path=SCISHEETS_PLUGIN_PYPATH):
    """
    Exports the table as python code
    :param Table table: table being processed
    :param str user_directory: directory where user functions are located
    :param str plug_directory: directory of common plugins
    """
    self._table = table
    self._user_directory = user_directory
    self._plugin_directory = plugin_directory
    self._plugin_path = plugin_path

  def makeEvaluationScriptProgram(self, create_API_object=False):
    """
    Creates a python script that evaluates the table formulas
    when there is a change to the scisheet
    :param bool create_API_object: True means that code will be generated
                                 that creates the API object.
    :return str program: Program as a string
    """
    sa = StatementAccumulator()
    # File Prologue
    statement = '''# Evaluation of the table %s.

    ''' % self._table.getName()
    sa.add(statement)
    sa.add(self._makePrologue())
    filepath = api_util.getTableCopyFilepath(self._table.getName(),
                                             self._user_directory)
    # Handle the API import
    statement = """
_table = api.getTableFromFile('%s')
%s = api.APIFormulas(_table) 
""" % (self._table.getFilepath(), API_OBJECT) 
    if not create_API_object:
      new_statement = statement.replace('\n', '\n#')
      header = "# Uncomment the following to execute standalone"
      statement = "%s\n#%s" % (header, new_statement)
    sa.add(statement)
    # Assign the column values to script variables
    sa.add(self._makeVariableAssignmentStatements())
    # Create the formula evaluation blocks
    sa.add(self._makeFormulaStatements())
    # Assign script variable to the column values
    sa.add(self._makeColumnValuesAssignmentStatements())
    return sa.get()

  def makeExportScriptProgram(self):
    """
    Creates an exported python script.
    :return str program: Program as a string
    """
    sa = StatementAccumulator()
    # File Prologue
    statement = '''# Script that runs formulas in the table %s.

    ''' % self._table.getName()
    sa.add(statement)
    sa.add(self._makePrologue())
    filepath = api_util.getTableCopyFilepath(self._table.getName(),
                                             self._user_directory)
    statement = """
_table = api.getTableFromFile('%s')
%s = api.APIFormulas(_table) 
""" % (filepath, API_OBJECT) 
    sa.add(statement)
    # Assign the column values to script variables
    sa.add(self._makeVariableAssignmentStatements())
    # Create the formula evaluation blocks
    sa.add(self._makeFormulaStatements())
    # Print the results
    sa.add(self._makeVariablePrintStatements())
    return sa.get()

  def _makeVariablePrintStatements(self):
    """
    Creates the print statements for all variables in the table.
    For each variable A:
      print ('A = %s' % str(A))
    :return str statements:
    """
    sa = StatementAccumulator()
    for column in self._table.getColumns():
      statement = """print ('%%s =  %%s' %% ("%s", str(%s))) """ %  \
          (column.getName(), column.getName())
      sa.add(statement)
    return sa.get()

  def makeFunctionProgram(self, function_name, inputs, outputs):
    """
    Creates a function for the table
    :param function_name: string name of the function to be created
    :param inputs: list of column names that are input to the function
    :param outputs: list of columns that are output from the function
    :return str program: Program as a string
    """
    # Initializations
    sa = StatementAccumulator()
    # Program Prologue
    statement = '''# Export of the table %s

    ''' % self._table.getName()
    sa.add(statement)
    sa.add(self._makePrologue())
    sa.add("")
    # Generate statements to create the API object
    statement = self._makeAPIPluginInitializationStatements(function_name)
    sa.add(statement)
    # Make the function definition
    sa.add(_makeFunctionStatement(function_name, inputs))
    sa.indent(1)
    # Assign the column values to function variables.
    # Note that inputs and outputs are not assigned.
    excludes = list(inputs)
    excludes.extend(outputs)
    sa.add(self._makeVariableAssignmentStatements(excludes=excludes))
    # Create the formula evaluation blocks
    sa.add(self._makeFormulaStatements())
    # Make the return statement
    sa.add(_makeReturnStatement(outputs))
    return sa.get()

  def makeTestProgram(self,
                          function_name=None,
                          inputs=None,
                          outputs=None):
    """
    Creates a program that tests the function exported for the table
    :param function_name: string name of the function to be created
    :param inputs: list of column names that are input to the function
    :param outputs: list of columns that are output from the function
    :return (str error, str program):
    """
    sa = StatementAccumulator()
    prefix = "self."
    output_str = _makeOutputStr(outputs)
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
    statement = self._makeAPIPluginInitializationStatements(function_name,
                                                            prefix=prefix)
    sa.add(statement)
    sa.indent(-1)
    # Construct the test function header
    sa.add("def testBasics(self):")
    sa.indent(1)
    # Assign values to the columns
    sa.add(self._makeVariableAssignmentStatements( \
        prefix=prefix, only_includes=inputs))
    # Construct the call to the function being tested
    statement =  _makeOutputStr(outputs)
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
    # Construct the program epilogue
    statement = """

if __name__ == '__main__':
  unittest.main()"""
    sa.add(statement)
    return sa.get()

  def _findFilenames(self, directory, suffix=PY_SUFFIX):
    """
    :param suffix: suffix to select
    :param str directory:
    :return: list of names of file names that have suffix (w/o suffix)
    """
    selected_filenames = []
    files = [f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))   \
           and f[-len(suffix):] == suffix]
    for name in files:
      is_valid_file = np.array([name.find(p, 0, len(p)) == -1
                    for p in IGNORE_PREFIX]).all()
      if is_valid_file:
        new_name = name[:len(name)-len(suffix)]
        selected_filenames.append(new_name)
    return selected_filenames

  #TODO: More robust approach to finding implied imports
  def _makeFormulaImportStatements(self, directory, import_path=""):
    """
    Construct import statements for the imports implied by the
    functions used in a formula. The approach taken isn't
    very robust:
      1. Find all .py files in the user's python directory. The
         function name should be the same as the file name.
      2. If a formula contains the file name (function name), then
         an import is generated.
    :param str directory: directory to search
    :param str import_path: path for the import
    :return str: import statements for files in the user directory
    """
    formulas = [c.getFormula() for c in self._table.getColumns()
                   if not (c.getFormula() is None)]
    python_filenames = self._findFilenames(directory)
    # Determine which files are referenced in a formula
    referenced_filenames = []
    for name in python_filenames:
      for formula in formulas:
        if name in formula:
          referenced_filenames.append(name)
          break
    # Construct the import statements
    sa = StatementAccumulator()
    for name in referenced_filenames:
      if len(import_path) == 0:
        sa.add("from %s import %s" % (name, name))
      else:
        sa.add("from %s.%s import %s" % (import_path, name, name))
    return sa.get()

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
    :return str: assignment statements
    """
    sa = StatementAccumulator()
    sa.add("# Assign column values to program variables.")
    full_object = "%s%s" % (prefix, API_OBJECT)
    columns = self._getSelectedColumns(**kwargs)
    for column in columns:
      name = column.getName()
      statement = "%s = %s.getColumnValues('%s')" %   \
          (name, full_object, name)
      sa.add(statement)
    return sa.get()

  def _makeColumnValuesAssignmentStatements(self, **kwargs):
    """
    Creates statements that assign column values to variables.
    Note that the assumption is that the variable name is the same
    as the column name
    """
    sa = StatementAccumulator()
    sa.add("\n")
    sa.add("# Assign program variables to columns values.")
    columns = self._getSelectedColumns(**kwargs)
    for column in columns:
      name = column.getName()
      statement = "%s.setColumnValues('%s', %s)" % (API_OBJECT, name, name)
      sa.add(statement)
    return sa.get()

  def _formulaColumns(self):
    """
    :return: list of columns that have a formula
    """
    return [fc for fc in self._table.getColumns()
            if fc.getFormula() is not None]

  def _makePrologue(self):
    """
    Creates the imports that go at the head of the file
    :return str: statements
    """
    # Initializations
    sa = StatementAccumulator()
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
    if self._user_directory is not None:
      statement = self._makeFormulaImportStatements(self._user_directory)
      sa.add(statement)
    statement = self._makeFormulaImportStatements(
        self._plugin_directory, import_path=self._plugin_path)
    sa.add(statement)
    return sa.get()

  # pylint: disable=R0913
  # pylint: disable=R0914
  # pylint: disable=R0915
  def _makeFormulaStatements(self):
    """
    Constructs a script to evaluate table formulas.
    :return str: statements
    Notes: (1) Iterate N (#formulas) times to handle dependencies
               between formulas
    """
    # Initializations
    sa = StatementAccumulator()
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
      # Ensure that there is at least one executeable statement
      sa.add("pass")  
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
        # Ensure that there is at least one executeable statement
        sa.add("pass")  
        sa.indent(-1)
        sa.add("except Exception as e:")
        sa.indent(1)
        sa.add("if nn == %d:" % (num_formulas-1))
        sa.indent(1)
        sa.add("raise Exception(e)")
        sa.add("break")
        sa.indent(-2)
    return sa.get()

  def _makeAPIPluginInitializationStatements(self, function_name, prefix=""):
    """
    :param str function_name:
    :param str prefix: prefix for API Object
    """
    full_object = "%s%s" % (prefix, API_OBJECT)
    filepath = api_util.getTableCopyFilepath(function_name,
                                             self._user_directory)
    statement = """%s = api.APIPlugin('%s')
%s.initialize()""" % (full_object, filepath, full_object)
    return statement

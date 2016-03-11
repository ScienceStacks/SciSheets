'''Evaluates formulas in a Table.'''

# Create name scopes for evaluation
import sys
from os import listdir
from os.path import isfile, join
# pylint: disable=W0611
import math as mt
import numpy as np
import pandas as pd
import random
import scipy as sp
import scipy.stats as ss

DEFAULT_FUNCTION_NAME = "MyFunction"
# Import files to ignore with these initial strings in their names
IGNORE_PREFIX = ['main_', 'test_', '__']
# Identifying python files
PY_SUFFIX = ".py"


class TableEvaluator(object):
  """
  Evaluates and otherwise processes formulas in a table
  """

  def __init__(self, table):
    # Inputs: table - table to evaluate
    self._table = table

  @staticmethod
  def _findFilenames(dir_path, suffix=PY_SUFFIX):
    """
    :param dir_path: directory path to search
    :param suffix: suffix to select
    :return: list of names of file names that have suffix (w/o suffix)
    """
    selected_filenames = []
    files = [f for f in listdir(dir_path)
        if isfile(join(dir_path, f)) and f[-len(suffix):] == suffix]
    for name in files:
      is_valid_file = np.array([name.find(p, 0, len(p)) == -1
                    for p in IGNORE_PREFIX]).all()
      if is_valid_file:
        new_name = name[:len(name)-len(suffix)]
        selected_filenames.append(new_name)
    return selected_filenames

  @staticmethod
  def _importStatements(user_directory, formula_columns):
    """
    :param user_directory: directory to search for user python files
    :param formula_columns: list of columns that have a formula
    :return: list of import statements for files in the user directory
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

  def _formulaColumns(self, exclude="!_%$#"):
    """
    :param exclude: string that, if present, excludes formula
    :return: list of columns that have a formula
    """
    return [fc for fc in self._table.getColumns()
            if fc.getFormula() is not None
              and exclude not in fc.getFormula()]

  # pylint: disable=R0913
  # pylint: disable=R0914
  # pylint: disable=R0915
  def _makeTableScript(self, user_directory=None, excluded_columns=None):
    """
    Constructs a script to evaluate a table.
    :param user_directory: directory where user functions are located
    :param excluded_columns: list of columns that are not initialized
    :return: list of statements constructed
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterate N (#formulas) times to handle dependencies
               between formulas
    """
    # Initializations
    indent = 0
    statements = []  # List of statements in the file
    if excluded_columns is None:
      excluded_columns = []
    formula_columns = self._formulaColumns()
    num_formulas = len(formula_columns)
    # Construct the imports
    import_statements = ['''
from _compare_arrays import compareArrays
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp

    ''']
    if user_directory is not None:
      import_statements.extend(
          TableEvaluator._importStatements(user_directory, formula_columns))
    statements.extend(TableEvaluator._indent(import_statements, indent))
    # Do the initial variable assignments
    assignment_statements = ["# Do initial assignments"]
    for column in self._table.getColumns():
      if not column.getName() in excluded_columns:
        statement = TableEvaluator._makeAssignment(column)
        assignment_statements.append(statement)
    statements.extend(TableEvaluator._indent(assignment_statements, indent))
    # Evaluate the formulas
    if len(formula_columns) > 0:
      statement = "#Evaluate the formulas"
      statements.extend(TableEvaluator._indent([statement], indent))
      statement = "for nn in range(%d):" % num_formulas
      statements.extend(TableEvaluator._indent([statement], indent))
      indent += 1
      for column in formula_columns:
        statement = "try:"
        statements.extend(TableEvaluator._indent([statement], indent))
        indent += 1
        statements.extend(TableEvaluator._indent(
            [column.getFormulaStatement()], indent))
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
      indent -= 1
    return statements

  def _makeUpdateDataStatements(self):
    """
    Write statements that update data in table columns
    :return: list of statements that construct a dict name "_results"
             with key of column name and value the column value
    """
    indent = 0
    statements = []
    statement = "_results = {}"
    statements.extend(TableEvaluator._indent([statement], indent))
    for column in self._table.getColumns():
      statement = "_results['%s'] = %s" % (column.getName(), column.getName())
      statements.extend(TableEvaluator._indent([statement], indent))
    return statements

  def evaluate(self, **kwargs):
    """
    Evaluates the formulas in a Table and assigns the _results
    to the formula columns
    :return: errors from execution or None
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterate N (#formulas) times to handle dependencies
               between formulas
    """
    indent = 0
    # Create the initial statements
    statements = self._makeTableScript(**kwargs)
    # Add statements to create the "_results" dict
    new_statements = self._makeUpdateDataStatements()
    statements.extend(TableEvaluator._indent(new_statements, indent))
    # Execute the statements
    # pylint: disable=W0122
    try:
      exec('\n'.join(statements), globals())  # Creates dict _results
    except Exception as err:
      # Report the error without changing the table
      return str(err)
    # Assign values to the table
    for key in _results.keys():
      column = self._table.columnFromName(key)
      self._table.updateColumn(column, _results[key])
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

  @staticmethod
  def _extractDtype(dtype):
    """
    Extracts the datatype to use in the column np.array
    Input: dtype - python data type
    Output: result - array data type
    """
    dtype_str = str(dtype)
    result = "object"
    try:
      ck_type = "float"
      dtype_str.index(ck_type)
      result = ck_type
    except ValueError:
      try:
        ck_type = "int"
        dtype_str.index(ck_type)
        result = ck_type
      except ValueError:
        try:
          dtype_str.index('|S')
          result = "'%s'" % dtype
        except ValueError:
          pass
    return result

  @staticmethod
  def _makeAssignment(column):
    """
    Returns an assignment statement that assigns the data values
    of a column to its column name.
    Input: column - Column object
    Output: statement - string assignment statement
    """
    statement = "%s = np.array(%s, dtype=%s)" % (
        column.getName(),
        str(column.getCells().tolist()),
        TableEvaluator._extractDtype(column.getDataType()))
    return statement

  # pylint: disable=R0913
  # pylint: disable=R0914
  # pylint: disable=R0915
  def export(self,
             function_name=None,
             inputs=None,
             outputs=None,
             file_path=None,
             user_directory=None):
    """
    Exports the table as python code
    Inputs: function_name - string name of the function to be created
            inputs - list of column names that are input to the function
            outputs - names of the columns that is output from the function
            file_path - path to the file to be written
            user_directory - directory where user functions are located
    Outputs: errror - errors from the export
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterate N (#formulas) times to handle dependencies
               between formulas
    """
    # Initializations
    if inputs is None:
      inputs = []
    if outputs is None:
      outputs = []
    indent = 0
    if function_name is None:
      function_name = DEFAULT_FUNCTION_NAME
    statements = []  # List of statements in the file
    formula_columns = self._formulaColumns(exclude=function_name)
    num_formulas = len(formula_columns)
    # File header
    header_comments = '''
# File generated as a SciSheets table export

    '''
    statements.extend(TableEvaluator._indent([header_comments], indent))
    # Construct the imports
    import_statements = ['''
from _compare_arrays import compareArrays
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp

    ''']
    if user_directory is not None:
      import_statements.extend(
          TableEvaluator._importStatements(user_directory, formula_columns))
    statements.extend(TableEvaluator._indent(import_statements, indent))
    # Function definition
    statement = "def %s(" % function_name
    statement += ",".join(inputs)
    statement += "):"
    statements.extend(TableEvaluator._indent([statement], indent))
    indent += 1

    # Do the initial variable assignments
    assignment_statements = ["# Do initial assignments"]
    for column in self._table.getColumns():
      if not column.getName() in inputs:
        statement = TableEvaluator._makeAssignment(column)
        assignment_statements.append(statement)
    statements.extend(TableEvaluator._indent(assignment_statements, indent))

    # Evaluate the formulas
    if len(formula_columns) > 0:
      statement = "#Evaluate the formulas"
      statements.extend(TableEvaluator._indent([statement], indent))
      statement = "for nn in range(%d):" % num_formulas
      statements.extend(TableEvaluator._indent([statement], indent))
      indent += 1
      for column in formula_columns:
        statement = "try:"
        statements.extend(TableEvaluator._indent([statement], indent))
        indent += 1
        statements.extend(TableEvaluator._indent(
            [column.getFormulaStatement()], indent))
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
      indent -= 1

    # Write the return statement
    output_str = ",".join(outputs)
    statement = "return %s" % output_str
    statements.extend(TableEvaluator._indent([statement], indent))

    # Write the test code
    indent = 0
    statement = '''
if __name__ == '__main__':'''
    statements.extend(TableEvaluator._indent([statement], indent))
    indent += 1
    test_statements = []
    for column_name in inputs:
      column = self._table.columnFromName(column_name)
      statement = TableEvaluator._makeAssignment(column)
      test_statements.append(statement)
    statement = output_str
    statement += " = %s(" % function_name
    statement += ",".join(inputs)
    statement += ")"
    test_statements.append(statement)
    statement = "b = True"
    test_statements.append(statement)
    for column_name in outputs:
      column = self._table.columnFromName(column_name)
      statement = "b and compareArrays(%s, %s)" % (
          column_name,
          str(column.getCells().tolist()))
      test_statements.append(statement)
    statement = "if b:"
    test_statements.append(statement)
    statement = "print ('OK.')"
    test_statements.extend(TableEvaluator._indent([statement], 1))
    statement = "else:"
    test_statements.append(statement)
    statement = "print ('Test failed for %s')" % function_name
    test_statements.extend(TableEvaluator._indent([statement], 1))
    statements.extend(TableEvaluator._indent(test_statements, indent))

    # Write the file
    if file_path is None:
      file_name = "%s.py" % function_name
      file_path = join(user_directory, file_name)
    with open(file_path, "w") as file_handle:
      file_handle.writelines(["%s\n" % s for s in statements])

'''Evaluates formulas in a Table.'''

# Create name scopes for evaluation
from util import findDatatypeForValues
from os import listdir
from os.path import isfile, join, dirname
import math as mt
import numpy as np
import pandas as pd
import random
import scipy as sp
import scipy.stats as ss
import string

DEFAULT_FUNCTION_NAME = "MyFunction"

class TableEvaluator(object):

  def __init__(self, table):
    # Inputs: table - table to evaluate
    self._table = table

  @staticmethod
  def _findPythonFiles(dir):
    # Inputs: dir - directory path to search
    # Output: list of python files that are valid
    #         user functions for scisheets
    PY_SUFFIX = ".py"
    python_files = []
    IGNORE_PREFIX = ['main_', 'test_', '__']
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    for f in files:
      b = np.array([f.find(p, 0, len(p)) == -1 
                    for p in IGNORE_PREFIX]).all() 
      if  b and f[-len(PY_SUFFIX):] == PY_SUFFIX:
        python_files.append(f)
    return python_files

  @staticmethod
  def _importStatements(user_directory, import_path):
    # Inputs: user_directory - directory to search for user python files
    #         import_path - path to import the file
    # Returns a list of import statements for files in the user directory
    python_files = TableEvaluator._findPythonFiles(user_directory)
    statements = []
    for f in python_files:
      if len(import_path) > 0:
        prefix = "%s." % import_path
      else:
        prefix = ""
      statement = "from %s%s import *" % (prefix, f[:-3])
      statements.append(statement)
    return statements

  def _formulaColumns(self):
    # Returns: formula_columns, non_formula_columns
    formula_columns = []
    non_formula_columns = []
    for column in self._table.getColumns():
      if column.getFormula() is None:
        non_formula_columns.append(column)
      else:
        formula_columns.append(column)
    return formula_columns, non_formula_columns

  def evaluate(self, user_directory=None, import_path=None):
    # Inputs: user_directory - directory where user functions are located
    #         import_path - import path for files in the user directory
    # Evaluates the formulas in a Table and assigns the results
    # to the formula columns
    # Outputs: errror - errors from execution or None
    # Notes: (1) Cannot put "exec" in another method
    #            since the objects created won't be accessible
    #        (2) Iterate N (#formulas) times to handle dependencies
    #            between formulas
    # Find the formula columns
    error = None
    formula_columns, _ = self._formulaColumns()
    num_formulas = len(formula_columns)
    # Get the user functions into the name space
    if user_directory is not None and import_path is not None:
      statements = TableEvaluator._importStatements(user_directory, 
                                                    import_path)
      for s in statements:
        try:
          exec(s)
        except Exception as e:
          return str(e)
    # Do the initial assignments
    for column in self._table.getColumns():
      statement = "%s = column.getCells()" % column.getName()
      try:
        exec(statement)
      except Exception as e:
        import pdb; pdb.set_trace()
       
    # Evaluate the formulas. Handle dependencies
    # by repeatedly evaluating the formulas
    for nn in range(num_formulas):
      for column in formula_columns:
        try:
          exec(column.getFormulaStatement())
          # Handle the case of a single value and consider
          # Assignments to other columns
#          if column.getName() in locals:
#            try:
#              _ = iter(column.getName())
#            except:
#              values = [column.getName()]
#          datatype = findDatatypeForValues(values)
#          assignment_statement = (
#              "%s = np.array(values, dtype=datatype)" % column.getName()
#              )
#          exec(assignment_statement)
        except Exception as e:
          if nn == num_formulas - 1:  # Only assign the error on the last loop
            error = "Error in formula %s: %s" % (column.getFormula(), str(e))
            break
    # Update the table
    # All columns are updated because there may be compound statements
    # that update non-formula columns
    for column in self._table.getColumns():
      statement = "new_values  = %s" % column.getName()
      exec(statement)
      self._table.updateColumn(column, new_values)
    return error
 
  @staticmethod 
  def _indent(statements, indent_level):
    # Inputs: statements - list of statements
    #         indent_level - integer level of indentation
    # Output: List of indented statements
    indents = " " * 2*indent_level
    result = []
    for s in statements:
      result.append("%s%s" % (indents, s))
    return result

  @staticmethod
  def _extractDtype(dtype):
    dtype_str = str(dtype)
    result = "object"
    try:
      ck_type = "float"
      dtype_str.index(ck_type)
      result = ck_type
    except:
      try:
        ck_type = "int"
        dtype_str.index(ck_type)
        result = ck_type
      except:
        try:
          dtype_str.index('|S')
          result = "'%s'" % dtype
        except:
          pass
    return result

  @staticmethod
  def _makeAssignment(column):
    statement = "%s = np.array(%s, dtype=%s)" % (
        column.getName(), 
        str(column.getCells().tolist()),
        TableEvaluator._extractDtype(column.getDataType()))
    return statement

  def export(self, 
             function_name=None,
             outputs=[],
             inputs=[],
             file_path=None,
             user_directory=None, 
             import_path=None):
    # Exports the table as python code
    # Inputs: function_name - string name of the function to be created
    #         outputs - names of the columns that is output from the function
    #         inputs - list of column names that are input to the function
    #         file_path - path to the file to be written
    #         user_directory - directory where user functions are located
    #         import_path - import path for files in the user directory
    # Outputs: errror - errors from the export
    # Notes: (1) Cannot put "exec" in another method
    #            since the objects created won't be accessible
    #        (2) Iterate N (#formulas) times to handle dependencies
    #            between formulas
    # Initializations
    indent = 0
    error = None
    if function_name is None:
      function_name = DEFAULT_FUNCTION_NAME
    statements = []  # List of statements in the file
    formula_columns, _ = self._formulaColumns()
    num_formulas = len(formula_columns)
    if user_directory is None:
      user_directory = dirname(__file__)
      import_path = ""
    # File header
    header_comments = '''
# File generated as a SciSheets table export

    '''
    statements.extend(TableEvaluator._indent([header_comments], indent))
    # Imports
    import_statements = ['''
from os import listdir
from os.path import isfile, join
import math as mt
import numpy as np
import pandas as pd
import scipy as sp

    ''']
    if user_directory is not None and import_path is not None:
      import_statements.extend(TableEvaluator._importStatements(user_directory, 
                                                                import_path))
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
      if not(column.getName() in inputs):
        statement = TableEvaluator._makeAssignment(column)
        assignment_statements.append(statement)
    statements.extend(TableEvaluator._indent(assignment_statements, indent))

    # Evaluate the formulas
    eval_statements = ["#Evaluate the formulas"]
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
      statement = "print('error in formula %s: '" % formula 
      statement += " + str(e))"
      statements.extend(TableEvaluator._indent([statement], indent))
      statement = "break"
      statements.extend(TableEvaluator._indent([statement], indent))
      indent -= 2

    # Write the return statement
    indent -= 1
    statement = "return "
    for nn in range(len(outputs)):
      if nn == len(outputs) - 1:
        suffix = ""
      else:
        suffix = ", "
      statement = "%s%s%s" % (statement, outputs[nn], suffix)
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
    statement = "%s(" % function_name
    statement += ",".join(inputs)
    statement += ")"
    full_statement = "print '%s=' + str(%s)" % (statement, statement)
    test_statements.append(full_statement)
    statements.extend(TableEvaluator._indent(test_statements, indent))
    
    # Write the file
    if file_path is None:
      file_name = "%s.py" % function_name
      file_path = join(user_directory, file_name)
    with open(file_path, "w") as f:
      f.writelines(["%s\n" % s for s in statements])

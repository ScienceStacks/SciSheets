'''Evaluates formulas in a Table.'''

# Create name scopes for evaluation
from util import findDatatypeForValues
from os import listdir
from os.path import isfile, join
import math as mt
import numpy as np

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
       
    for nn in range(num_formulas):
      # Evaluate the formulas
      for column in formula_columns:
        # Create the full statement so that a formula can contain
        # other assignment statements
        formula = column.getFormula()
        formula_statement = "values = %s" % formula
        try:
          exec(formula_statement)
          # Handle the case of a single value
          try:
            _ = iter(values)
          except:
            values = [values]
          datatype = findDatatypeForValues(values)
          assignment_statement = (
              "%s = np.array(values, dtype=datatype)" % column.getName()
              )
          exec(assignment_statement)
        except Exception as e:
          if nn == num_formulas - 1:  # Only assign the error on the last loop
            error = "Error in formula %s: %s" % (formula, str(e))
            break
    # Update the table
    # All columns are updated because there may be compound statements
    # that update non-formula columns
    for column in self._table.getColumns():
      statement = "new_values  = %s" % column.getName()
      exec(statement)
      self._table.updateColumn(column, new_values)
    return error

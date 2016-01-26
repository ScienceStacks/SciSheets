'''Evaluates formulas in a Table.'''

# Create name scopes for evaluation
import math as m
import numpy as n

class TableEvaluator(object):

  def __init__(self, table):
    self.table = table

  def evaluate(self):
    # Evaluates the formulas in a Table and assigns the results
    # to the formula columns
    # Outputs: errror - errors from execution or None
    # Notes: (1) Cannot put "exec" in another method
    #            since the objects created won't be accessible
    #        (2) Iterate N (#formulas) times to handle dependencies
    #            between formulas
    # Find the formula columns
    formula_columns = []
    for column in self.table.getColumns():
      if column.getFormula() is not None:
        formula_columns.append(column)
    num_formulas = len(formula_columns)
    error = None
    for nn in range(num_formulas):
      # Assign the values on each iteration
      for column in self.table.getColumns():
        statement = "%s = column.getCells()" % column.getName()
        exec(statement)
      # Evaluate the formulas
      for column in formula_columns:
        formula = column.getFormula()
        try:
          values = eval(formula)
          column.addCells(values, replace=True)
          statement = "%s = column.getCells()" % column.getName()
          exec(statement)
        except Exception as e:
          if nn == num_formulas - 1:  # Only assign the error on the last loop
            error = "Error in formula %s: %s" % (formula, str(e))
            break
    return error

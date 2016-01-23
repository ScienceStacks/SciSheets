'''Evaluates formulas in a Table.'''

# Create name scopes for evaluation
import math as m
import numpy as n
#import pandas as p

class TableEvaluator(object):

  def __init__(self, table):
    self.table = table

  def evaluate(self):
    # Evaluates the formulas in a Table and assigns the results
    # to the formula columns
    # Outputs: errror - errors from execution or None
    # Notes: (1) Cannot put "exec" in another method
    #            since the objects created won't be accessible
    error = None
    for column in self.table.getColumns():
      statement = "%s = column.getCells()" % column.getName()
      exec(statement)
    for column in self.table.getColumns():
      formula = column.getFormula()
      if formula is not None:
        try:
          values = eval(formula)
          column.addCells(values, replace=True)
          statement = "%s = column.getCells()" % column.getName()
          exec(statement)
        except Exception as e:
          error = "Error in formula %s: %s" % (formula, str(e))
          break
    return error

"""
   Abstracts a column to handle its existence as both part of a Table and
   a namespace variable.
   Issues:
   1. Consistency for the use of padding values so can do comparisons and
      do vector operations.
"""

import api_util


class ColumnVariable(object):
  """
  Manages the relationship between the data in a Column and a namespace variable
  with the same name. This is done in the context of formula evaluation, especially
  iterative evaluation of formulas.
  The ColumnVariable assumes that the underlying table is not updated.
  If the underlying table is to be updated:
    1. use setColumnValue() to update the column from the namespace variable
    2. Make the table modifications
    3. Create a new ColumnVariable.
  """


  def __init__(self, column):
    """
    :param Column column:
    """
    self._column = column
    self._baseline_value = None
    self._iteration_start_value = None
    self.setBaselineValue()
    self._setNamespaceValue()
    self.setIterationStartValue()
 
  def getNamespaceValue(self):
    return self._column.getTable().getNamespace()[self._column.getName()]

  def getColumnValue(self):
    return self._column.getCells()

  def _setNamespaceValue(self):
    """
    Establishes the value of the variable in the namespace.
    """
    table = self._column.getTable()
    table.getNamespace()[self._column.getName()] = self.getColumnValue()

  def setColumnValue(self):
    """
    Establishes the value of the variable in the Column.
    Called if the column is changed outside the namespace during
    formula evaluation.
    :param object value:
    """
    self._column.addCells(self.getNamespaceValue(), replace=True)

  def setIterationStartValue(self):
    """
    Establishes the value of the variable in the namespace at the
    start of an iteration in formula evaluation.
    """
    self._iteration_start_value = self.getNamespaceValue()

  def setBaselineValue(self):
    """
    Sets the baseline values from the column values.
    """
    self._baseline_value = self.getColumnValue()

  def isChangedFromBaselineValue(self):
    """
    Checks if the value of the variable in the namespace
    has changed from its baselineline value.
    :return bool: True if changed
    """
    return api_util.isEquivalentData(self.getNamespaceValue(), self._baseline_value)

  def isChangedFromIterationStartValue(self):
    """
    Checks if the value of the variable in the namespace
    has changed from its iteration start value
    :return bool: True if changed
    """
    return api_util.isEquivalentData(self.getNamespaceValue(), self._iteration_start_value)

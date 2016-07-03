"""
   Abstraction for values of columns that encompasses both their representation
   in Columns and in the namespace used for table evaluation.
   the execution namespace.
"""

import api_util


class ColumnVariable(object):

  def __init__(self, column):
    """
    :param Column column:
    """
    self._column = column
    self._baseline_value = None
    self._iteration_start_value = None
    self.setBaselineValue()
    self._setNamespaceValue(self._baseline_value)
 
  def getNamespaceValue(self):
    return self._column.getTable().getNamespace()[self._column.getName()]

  def getColumnValue(self):
    return self._column.prunedCells()

  def _setNamespaceValue(self, values):
    """
    Establishes the value of the variable in the namespace.
    :param list values:
    """
    table = self._column.getTable()
    table.getNamespace()[self._column.getName()] = values

  def setIterationStartValue(self, values):
    """
    Establishes the value of the variable in the namespace at the
    start of an iteration in formula evaluation.
    :param list values:
    """
    table = self._column.getTable()
    table.getNamespace()[self._column.getName()] = values

  def setBaselineValue(self):
    """
    Sets the baseline reference values from the column values.
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

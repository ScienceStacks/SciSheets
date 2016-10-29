"""
   Abstracts a column to handle its existence as both part of a Table and
   a namespace variable. A ColumnVariable has a lifetime no longer than the
   period that the underlying column is static.
"""

import api_util
import cell_types


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
    self._baseline_value = self.getColumnValue()
    self._setNamespaceValue()
    self._iteration_start_value = self.getNamespaceValue()

  def getNamespaceValue(self):
    if self._column.getTable() is None:
      import pdb; pdb.set_trace()
    # TODO: This won't work with nested columns - consider namespaces
    return self._column.getTable().getNamespace()[self._column.getName()]

  def getColumn(self):
    return self._column

  def getName(self):
    # TODO: This won't work with nested columns - consider namespaces
    return self._column.getName()

  def getColumnValue(self):
    return self._column.getCells()

  def _setNamespaceValue(self):
    """
    Establishes the value of the variable in the namespace.
    """
    table = self._column.getTable()
    # TODO: This won't work with nested columns - consider namespaces
    table.getNamespace()[self._column.getName()] =  \
        api_util.coerceValuesForColumn(self._column, 
                                       self.getColumnValue())

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

  def isNamespaceValueEquivalentToBaselineValue(self):
    """
    Checks if the value of the variable in the namespace
    has changed from its baselineline value.
    :return bool: True if changed
    """
    return cell_types.isEquivalentData(self.getNamespaceValue(), self._baseline_value)

  def isNamespaceValueEquivalentToIterationStartValue(self):
    """
    Checks if the value of the variable in the namespace
    has changed from its iteration start value
    :return bool: True if changed
    """
    return cell_types.isEquivalentData(self.getNamespaceValue(), self._iteration_start_value)

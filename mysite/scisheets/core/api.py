"""
The API provides runtime support for user execution. There are two runtime environments:
(a) evaluation of the formulas in a Table object and (b) execution of a standalone
python program that was exported from a Table object.
The API consists of these parts: 
  1. APIFormulas provides extended capabilities for executing formulas
  2. APIPlugin provides runtime support for standalone execution
  3. API base clase provides common code.
The API is intended to be sparse in that it focuses on table manipulation.
Plugins may use the API to do data manipulation and calculations.

The argument to many API methods are column variables, such as
ExtendedArray. Column variables must have a public name property,
which is the column name.
"""

from column import Column
from table import Table, NAME_COLUMN_STR
import helpers.api_util as api_util
from helpers.column_variable import ColumnVariable
from helpers.block_execution_controller import BlockExecutionController
import helpers.cell_types as cell_types
from helpers.extended_array import ExtendedArray
from helpers.combinatoric_list import CombinatoricList
import collections
import os
import numpy as np
import pandas as pd
import pickle

################### FUNCTIONS
def getTableFromFile(file_path):
  return api_util.getTableFromFile(file_path)


################### CLASSES
class API(object):
  """
  Code that is common to the formulas and plugin APIs.
  Usage:
  """

  def __init__(self, is_logging=False):
    self._is_logging = is_logging
    self._column_variables = []
    self.setTable(None)  # self._table
    self._column_idx = None
    self._table_filepath = None
    # Columns excluded from update because created dynamically
    # and so the user has responsibility for their update
    self._exclude_column_update = []

  def setTable(self, table):
    self._table = table
    self.setColumnVariables()
    self.controller = BlockExecutionController(self, 
        is_logging=self._is_logging)

  def _dbgCheckColumnVariables(self):
    for cv in self._column_variables:
      if cv._column._owning_table is None:
        import pdb; pdb.set_trace()

  def setColumnVariables(self, colnms=None):
    """
    Creates ColumnVariables for each column in the table
    :param list-of-str colnms: If not None, then only set
                               the named ColumnVariables
    """
    # No Table
    if self._table is None:
      self._column_variables = []
      return
    # Table present
    cv_dict = {}
    for column in  self._table.getColumns():
      name = column.getName()
      cv = self.getColumnVariable(name)
      cv_dict[name] = cv
    if colnms is None:
      colnms = [c.getName() for c in self._table.getColumns()]
    for colnm in colnms:
      column = self._table.columnFromName(colnm)
      if column is None:
        import pdb; pdb.set_trace()
      if column._owning_table is None:
        import pdb; pdb.set_trace()
      cv_dict[colnm] = ColumnVariable(column)
    self._column_variables = cv_dict.values()
    self._dbgCheckColumnVariables()
  
  def getColumnVariable(self, colnm):
    for cv in self._column_variables:
      if cv.getColumn().getName() == colnm:
        return cv
    return None

  def getColumnVariables(self):
    return self._column_variables

  def updateColumnFromColumnVariables(self, colnms=None):
    """
    Updates the column variables that have changed.
    :param list-of-str colnms:
    """
    if colnms is None:
      colnms = [cv.getName() for cv in self._column_variables]
    for cv in self._column_variables:
      if cv.getName() in colnms:
        if not cv.isNamespaceValueEquivalentToBaselineValue():
          cv.setColumnValue()

  def addColumnsToTableFromDataframe(self, 
                                     dataframe, 
                                     names=None, 
                                     column_position=None):
    """
    Adds columns from a dataframe to the table. If a column of the same
    name exists, its data is replaced.
    :param pandas.DataFrame dataframe:
    :param list-of-str names: names of columns in the dataframe
        to include. Default (None) is all.
    :param str column_position: name of the column to place after
    :return list-of-str names: names of columns added to the table
    """
    self.updateColumnFromColumnVariables()  # Make sure table is current
    if names is None:
      names = list(dataframe.columns)
    if column_position is None:
      index = self._table.numColumns()
    else:
      column = self._table.columnFromName(column_position)
      index = self._table.indexFromColumn(column) + 1
    for name in names:
      if self._table.isColumnPresent(name):
        column = self._table.columnFromName(name)
      else:
        column = Column(name)
        self._table.addColumn(column, index=index)
        index += 1
      column.addCells(dataframe[name], replace=True)
      if column._owning_table is None:
        import pdb; pdb.set_trace()
        pass
    self.setColumnVariables()
    return names

  def dataframeToTable(self, table_name, dataframe, names=None):
    """
    Creates a Table from the pandas dataframe.
    :param str table_name: name of the table
    :param pd.DataFrame dataframe:
    :param list-of-str names: names of names in the dataframe
                                that are names in the table.
                                Defaull is all.
    :return Table table:
    """
    if names is None:
      names = list(dataframe.columns)
    table = Table(table_name)
    for name in names:
      column = Column(name)
      column.addCells(dataframe[name], replace=True)
      table.addColumn(column)
    return table 

  def coerceValues(self, column_name, values):
    """
    Coerces the values to the type appropriate for the column
    :param str column_name: name of the column
    :return: type appropriate for column
    :raises: ValueError
    """
    column = self.getColumn(column_name)
    return api_util.coerceValuesForColumn(column, values)

  def getColumn(self, column_id, validate=True):
    """
    :param column_id: either the name of the column or
                      its 1-based index after the name ('row') column
    :param bool validate: Validates the columns present if True
    :return: column object
    :raises: ValueError if column_name doesn't exist
    """
    if isinstance(column_id, int):
      column = self._table.columnFromIndex(column_id)
    elif cell_types.isStr(column_id):
      column = self._table.columnFromName(column_id)
    else:
      column = None
    if column is None and validate:
      import pdb; pdb.set_trace()
      raise ValueError("%s column does not exist." % str(column_id))
    return column

  def getColumnNames(self):
    """
    :return list-of-str:
    """
    return [c.getName() for c in self._table.getColumns()]

  def _getColumnValue(self, column_name):
    """
    :param str column_name: name of the column
    :return: iterable of object
    :raises: ValueError
    """
    column = self.getColumn(column_name)
    return api_util.coerceValuesForColumn(column, column.getCells())

  def getColumnValue(self, column_name):
    """
    :param str column_name: name of the column
    :return: iterable of object
    :raises: ValueError
    """
    column = self.getColumn(column_name)
    return api_util.coerceValuesForColumn(column, column.getCells())

  def getTable(self):
    return self._table

  #TODO: Eliminate column_name since have an ExtendedArray
  def setColumnVisibility(self, column_names=None, is_visible=True):
    """
    Sets whether the column is visible
    :param list-of-str column_names: default is all columns
    :param bool is_visible: set to unhidden if True; otherwise hidden
    :raises ValueError: column name not found
    """
    if column_names is None:
      column_names = [c.getName() for c in self._table.getColumns()]
    columns = []
    for name in column_names:
      column = self._table.columnFromName(name)
      if column is None:
        raise ValueError("Column %s not found" % name)
      columns.append(column)
    if is_visible:
      self._table.unhideColumns(columns)
    else:
      self._table.hideColumns(columns)

  def setColumnValue(self, column_name, values):
    """
    :param str column_name: name of the column
    :param iterable-of-object values:
    :raises: ValueError
    """
    if column_name in self._exclude_column_update:
      return
    if not self._table.isColumnPresent(column_name):
      return
    column = self._table.columnFromName(column_name)
    if column is None:
      raise ValueError("Column name not found: %s" % column_name)
    if isinstance(values, list):
      list_values = values
    elif "tolist" in dir(values):
      list_values = values.tolist()
    else:
      list_values = list(values)
    self._table.updateColumn(column, list_values)

  def tableToDataframe(self, columns=None):
    """
    Creates a dataframe from columns in the table.
    :param list-of-str columns: column columns to include. Default is all.
    :return pandas.DataFrame:
    :raises ValueError: invalid column name
    Does not export the "name column"
    """
    if columns is None:
      columns = [c.getName() for c in self._table.getDataColumns()]
    dataframe = pd.DataFrame()
    for name in columns:
      column = self._table.columnFromName(name)
      if column is None:
        raise ValueError("Column %s does not exist in table %s" %  \
            (name, self._table.getName()))
      dataframe[name] = column.getCells()
    return dataframe

  def updateTableFile(self):
    api_util.writeTableToFile(self._table)


class APIFormulas(API):
  """
  The API extends formulas with: Trinary logic, creation of scalar 
  parameters, creation and deletion of columns.
     S = APIFormulas(table)
  Key concepts:
    column_id - either the column name or column index
  """

  def __init__(self, table, is_logging=False):
    """
    :param Table table: table for which execution is done
    """
    super(APIFormulas, self).__init__(is_logging=is_logging)
    self.setTable(table)

  def _createColumn(self, column_name, index=None, asis=False):
    """
    Creates a new column, either just to the right of the
    current column (index=None) are at a specific index.
    :param str column_name: name of the column to create
    :param int index: index where the column is to be placed
    :param bool asis: Column data should not be coerced
    :return: column object
    :raises: ValueError if invalid name for column
    """
    if self._table.isColumnPresent(column_name):
      return self._table.columnFromName(column_name)
    # Create the column
    column = Column(column_name, asis=asis)
    error = self._table.addColumn(column, index)
    if error is not None:
      raise ValueError(error)
    return column

  def createColumn(self, column_name, index=None, asis=False):
    """
    Creates a new column, either just to the right of the
    current column (index=None) are at a specific index.
    :param str column_name: name of the column to create
    :param int index: index where the column is to be placed
    :return: column object
    """
    return self._createColumn(column_name, 
                              index=index,
                              asis=asis)

  def deleteColumn(self, column_id):
    """
    Detes an existing a column if it exists.
    :param column_id: either the name of the column or 
                      the 1-based index after the 'row' column
    """
    column = self.getColumn(column_id, validate=False)
    if column is not None:
      _  = self._table.deleteColumn(column)
      self.setColumnVariables()

  def updateTableCellsAndColumnVariables(self, excludes):
    """
    Updates data in tables based on the values of the corresponding
    column variable, if one exists. Creates column variables for
    columns that do that have one.
    :param list-of-str excludes: table columns that are not updated
    """
    namespace = self._table.getNamespace()
    for column in self._table.getColumns():
      name = column.getName()
      if not name in excludes:
        if name in namespace:
          self.setColumnValue(name, namespace[name])
        else:
          namespace[name] = self._getColumnValue(name)

class APIPlugin(APIFormulas):
  """
  Support for running standalone codes
     S = APIPlugin(table_filepath)
     S.initialize()
  """

  def __init__(self, table_filepath, is_logging=True):
    """
    :param str table_filepath: full path to the table file
    """
    super(APIPlugin, self).__init__(None)
    self._table_filepath = table_filepath

  def initialize(self):
    """
    Does initialization at the beginning of executing table
    code.
    """
    table = api_util.getTableFromFile(self._table_filepath,
      verify=False)
    self.setTable(table)
    self.controller.setTable(self._table)

  def compareToColumnValues(self, column_name, values):
    """
    Compares the values to those in the column.
    :param str column_name:
    :param object values:
    :return bool: True if successful comparison
    """
    column = self._table.columnFromName(column_name)
    return api_util.compareIterables(column.getCells(), values)


class APIAdmin(APIPlugin):
  """
  Support for running standalone codes
     S = APIPlugin(table_filepath)
     S.initialize()
  """

  def __init__(self, table_filepath):
    """
    :param str table_filepath: full path to the table file
    """
    super(APIAdmin, self).__init__(None)
    self._table_filepath = table_filepath

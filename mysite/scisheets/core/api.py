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

Two types of names are used:
    colnm: the name of the python variable for the column
    nodnm: the (global) name of the column in the tree for the Table.
           By a global name is meant a complete path in the Table tree.
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
def readTableFromFile(file_path):
  return api_util.readObjectFromFile(file_path)


################### CLASSES
class API(object):
  """
  Code that is common to the formulas and plugin APIs.
  Usage:
  """

  def __init__(self, is_logging=False, debug=False):
    self.debug = debug # Used for conditional debugging
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
        is_logging=self._is_logging, debug=self.debug)

  def _dbgCheckColumnVariables(self):
    for cv in self._column_variables:
      if cv._column is None:
        import pdb; pdb.set_trace()
      if cv._column.getParent() is None:
        import pdb; pdb.set_trace()

  def setColumnVariables(self, nodenms=None):
    """
    Creates ColumnVariables for each column specified.
    :param list-of-str nodenms: If not None, then only set
                               the named ColumnVariables
    """
    if nodenms is None:
      # Gets the nodenm for all data containing columns
      nodenms = []
      if self._table is not None:
        nodenms = [c.getName()
            for c in self._table.getDataColumns(is_attached=False, 
            is_recursive=True)]
    # No Table
    if self._table is None:
      self._column_variables = []
      return
    # Table present
    cv_dict = {cv._column.getName(): cv 
               for cv in self._column_variables
               if not cv._column.isRoot()}
    for nodenm in nodenms:
      column = self._table.childFromName(nodenm, is_relative=False)
      if column is None:
        import pdb; pdb.set_trace()
      if not isinstance(column, Column):
        import pdb; pdb.set_trace()
      if column.isRoot():
        import pdb; pdb.set_trace()
      cv_dict[nodenm] = ColumnVariable(column)
    self._column_variables = cv_dict.values()
    self._dbgCheckColumnVariables()
  
  def getColumnVariable(self, colnm):
    column_variables = [cv for cv in self._column_variables
         if cv.getColumn().getName(is_global_name=False) == colnm]
    if len(column_variables) == 0:
      raise RuntimeError("Column variable not found for %s" % colnm)
    elif len(column_variables) == 1:
      return column_variables[0]
    else:
      raise RuntimeError("Multiple column variable found for %s" % colnm)

  def _columnFromColnm(self, colnm):
    """
    Returns to Column corresponding to the column name.
    :param str colnm:
    :return Column:
    """
    cv = self.getColumnVariable(colnm)
    return cv.getColumn()

  def getColumnVariables(self):
    return self._column_variables

  # TODO: Test
  def updateColumnFromColumnVariables(self, nodenms=None):
    """
    Updates the column variables that have changed.
    :parm list-of-str nodenms: Global names of nodes corresponding
        to the ColumnVariables
    :param list-of-str colnms:
    """
    if nodenms is None:
      nodenms = [cv.getName() 
                for cv in self._column_variables]
    for cv in self._column_variables:
      if cv.getName() in nodenms:
        if not cv.isNamespaceValueEquivalentToBaselineValue():
          cv.setColumnValue()

  # TODO: Test - can specify a table to which data are added
  def addColumnsToTableFromDataframe(self, 
                                     dataframe, 
                                     names=None, 
                                     column_position=None,
                                     table=None):
    """
    Adds columns from a dataframe to a table. If a column of the same
    name exists, its data is replaced.
    :param pandas.DataFrame dataframe:
    :param list-of-str names: names of columns in the dataframe
        to include. Default (None) is all.
    :param str column_position: name of the column to place after
    :return list-of-str names: names of columns added to the table
    """
    if table is None:
      table = self._table
    self.updateColumnFromColumnVariables()  # Make sure table is current
    if names is None:
      names = list(dataframe.columns)
    index = table.numColumns()  # Where to insert new columns
    if column_position is not None:
      column = table.columnFromName(column_position)
      index = table.indexFromColumn(column) + 1
    for name in names:
      if table.isColumnPresent(name):
        column = table.columnFromName(name)
      else:
        if "." in name:
          import pdb; pdb.set_trace()
        column = Column(name)
        table.addColumn(column, index=index)
        index += 1
      column.addCells(dataframe[name], replace=True)
      if column.getParent() is None:
        import pdb; pdb.set_trace()
        pass
    root_table = table.getRoot(is_attached=False)
    root_table.adjustColumnLength()
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

  def coerceValues(self, colnm, values):
    """
    Coerces the values to the type appropriate for the column
    :param str colnm: global name of the column
    :return: type appropriate for column
    :raises: ValueError
    """
    column = self.getColumn(colnm)
    return api_util.coerceValuesForColumn(column, values)

  def getColumn(self, column_id, validate=True):
    """
    :param column_id: either the global column name or
                      its 1-based index after the name ('row') column
    :param bool validate: Validates the columns present if True
    :return: column object
    :raises: ValueError if column_name doesn't exist
    """
    if isinstance(column_id, int):
      column = self._table.columnFromIndex(column_id)
    elif cell_types.isStr(column_id):
      column = self._columnFromColnm(column_id)
    else:
      column = None
    if column is None and validate:
      import pdb; pdb.set_trace()
      raise ValueError("%s column does not exist." % str(column_id))
    return column

  def getColumnNames(self):
    """
    :return list-of-colnm: 
    """
    return [c.getName(is_global_name=False) 
            for c in self._table.getDataColumns()]

  def getColumnValue(self, colnm):
    """
    :param str colnm: name of the column
    :return: iterable of object
    :raises: ValueError
    """
    column = self.getColumn(colnm)
    return api_util.coerceValuesForColumn(column, column.getCells())

  def getTable(self):
    return self._table

  #TODO: Eliminate column_name since have an ExtendedArray
  # TODO: Changed
  def setColumnVisibility(self, nodenms=None, is_visible=True):
    """
    Sets whether the column is visible based on its node name.
    :param list-of-str nodenms: default is all columns
    :param bool is_visible: set to unhidden if True; otherwise hidden
    :raises ValueError: column name not found
    """
    if nodenms is None:
      nodenms = [c.getName() for c in self._table.getColumns()]
    columns = []
    for name in nodenms:
      column = self._table.columnFromName(name)
      if column is None:
        raise ValueError("Column %s not found" % name)
      columns.append(column)
    if is_visible:
      self._table.unhideChildren(columns)
    else:
      self._table.hideChildren(columns)

  # TODO: Changed
  def setColumnValue(self, colnm, values):
    """
    :param str colnm: name of the column
    :param iterable-of-object values:
    :raises: ValueError
    """
    if colnm in self._exclude_column_update:
      return
    if not colnm in self.getColumnNames():
      return
    column = self._columnFromColnm(colnm)
    if column is None:
      raise ValueError("Column name not found: %s" % colnm)
    if isinstance(values, list):
      list_values = values
    elif "tolist" in dir(values):
      list_values = values.tolist()
    else:
      list_values = list(values)
    self._table.updateColumn(column, list_values)

  def tableToDataframe(self, colnms=None):
    """
    Creates a dataframe from columns in the table.
    :param list-of-str colnms: column names to include. Default is all.
    :return pandas.DataFrame:
    :raises ValueError: invalid column name
    Does not export the "name column"
    """
    if colnms is None:
      colnms = [c.getName() for c in self._table.getDataColumns()]
    dataframe = pd.DataFrame()
    for name in colnms:
      column = self._table.childFromName(name, is_relative=False)
      if column is None:
        raise ValueError("Column %s does not exist in table %s" %  \
            (name, self._table.getName()))
      dataframe[name] = column.getCells()
    return dataframe

  def updateTableFile(self):
    api_util.writeObjectToFile(self._table)


class APIFormulas(API):
  """
  The API extends formulas with: Trinary logic, creation of scalar 
  parameters, creation and deletion of columns.
     S = APIFormulas(table)
  Key concepts:
    column_id - either the column name or column index
  """

  def __init__(self, table, is_logging=False, debug=False):
    """
    :param Table table: table for which execution is done
    """
    super(APIFormulas, self).__init__(is_logging=is_logging,
        debug=debug)
    self.setTable(table)

  # TODO: Changed
  def _createColumn(self, colnm, index=None, 
      asis=False, table=None):
    """
    Creates a new column, either just to the right of the
    current column (index=None) are at a specific index.
    :param str colnm: name of the column to create
    :param int index: index where the column is to be placed
    :param bool asis: Column data should not be coerced
    :param Table table: Table on which operation is performed
    :return: column object
    :raises: ValueError if invalid name for column
    """
    if table is None:
      table = self._table
    if table.isColumnPresent(colnm):
      return table.columnFromName(colnm)
    # Create the column
    column = Column(colnm, asis=asis)
    error = table.addColumn(column, index)
    if error is not None:
      raise ValueError(error)
    self.setColumnVariables(nodenms=[column.getName()])
    return column

  # TODO: Changed
  def createColumn(self, colnm, index=None, asis=False, tablenm=None):
    """
    Creates a new column, either just to the right of the
    current column (index=None) are at a specific index.
    :param str colnm: name of the column to create
    :param int index: index where the column is to be placed
    :param str tablenm: global name of the table for the Column
    :return: column object
    """
    if tablenm is None:
      tablenm = self._table.getName()
    table = self._table.childFromName(tablenm)
    return self._createColumn(colnm, 
                              index=index,
                              asis=asis,
                              table=table)

  def deleteColumn(self, column_id):
    """
    Detes an existing a column if it exists.
    :param column_id: either the name of the column or 
                      the 1-based index after the 'row' column
    """
    column = self.getColumn(column_id, validate=False)
    if column is not None:
      _  = column.removeTree()
      self.setColumnVariables()

  # TODO: Changed
  def updateTableCellsAndColumnVariables(self, excludes):
    """
    Updates data in tables based on the values of the corresponding
    column variable, if one exists. Creates column variables for
    columns that do that have one.
    :param list-of-str excludes: table columns that are not updated
    """
    namespace = self._table.getNamespace()
    for column in self._table.getDataColumns():
      name = column.getName(is_global_name=False)
      if not name in excludes:
        if name in namespace:
          self.setColumnValue(name, namespace[name])
        else:
          namespace[name] = self.getColumnValue(name)

class APIPlugin(APIFormulas):
  """
  Support for running standalone codes
     S = APIPlugin(table_filepath)
     S.initialize()
  """

  def __init__(self, table_filepath, is_logging=True, debug=False):
    """
    :param str table_filepath: full path to the table file
    """
    super(APIPlugin, self).__init__(None, debug=debug)
    self._table_filepath = table_filepath

  def initialize(self):
    """
    Does initialization at the beginning of executing table
    code.
    """
    table = api_util.readObjectFromFile(self._table_filepath,
      verify=False)
    self.setTable(table)
    self.controller.setTable(self._table)

  # TODO: Changed
  def compareToColumnValues(self, colnm, values):
    """
    Compares the values to those in the column.
    :param str colnm:
    :param object values:
    :return bool: True if successful comparison
    """
    column = self._table.columnFromName(colnm)
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

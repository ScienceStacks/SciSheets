"""
The API provides runtime support for user execution. There are two runtime environments:
(a) evaluation of the formulas in a Table object and (b) execution of a standalone
python program that was exported from a Table object.
The API consists of these parts: 
  1. APIFormulas provides extended capabilities for executing formulas (e.g., trinary logical operations
     and truth tables)
  2. APIPlugin provides runtime support for standalone execution
  3. API base clase provides common code.
"""

from column import Column
from table import Table
import util.api_util as api_util
from util.trinary import Trinary
from util.combinatoric_list import CombinatoricList
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

  def __init__(self):
    self._table = None
    self._column_idx = None
    self._table_filepath = None

  def _coerceValues(self, column, values):
    """
    Coerces the values to the type appropriate for the column
    :param Column column:
    :return: type appropriate for column
    :raises: ValueError
    """
    data_class = column.getDataClass()
    return data_class.cons(values)

  def coerceValues(self, column_name, values):
    """
    Coerces the values to the type appropriate for the column
    :param str column_name: name of the column
    :return: type appropriate for column
    :raises: ValueError
    """
    column = self._getColumn(column_name)
    return self._coerceValues(column, values)

  def _getColumn(self, column_id, validate=True):
    """
    :param column_id: either the name of the column or
                      its 1-based index after the name ('row') column
    :param bool validate: Validates the columns present if True
    :return: column object
    :raises: ValueError if column_name doesn't exist
    """
    if isinstance(column_id, int):
      column = self._table.columnFromIndex(column_id)
    elif isinstance(column_id, str):
      column = self._table.columnFromName(column_id)
    else:
      column = None
    if column is None and validate:
      raise ValueError("%s column does not exist." % str(column_id))
    return column

  def getColumnNames(self):
    """
    :return list-of-str:
    """
    return [c.getName() for c in self._table.getColumns()]


  def getColumnValues(self, column_name):
    """
    :param str column_name: name of the column
    :return: iterable of object
    :raises: ValueError
    """
    column = self._getColumn(column_name)
    return self._coerceValues(column, column.getCells())

  def getTable(self):
    return self._table

  def setColumnValues(self, column_name, values):
    """
    :param str column_name: name of the column
    :param iterable-of-object values:
    :raises: ValueError
    """
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

  def updateTableFile(self):
    api_util.writeTableToFile(self._table.getFilepath())


class APIFormulas(API):
  """
  The API extends formulas with: Trinary logic, creation of scalar 
  parameters, creation and deletion of columns.
     S = APIFormulas(table)
  Key concepts:
    column_id - either the column name or column index
  """

  def __init__(self, table):
    """
    :param Table table: table for which execution is done
    """
    super(APIFormulas, self).__init__()
    self._table = table

  def createTruthTable(self, column_names, only_boolean=False):
    """
    Creates a truth table with all combinations of Boolean
    values for the number of columns provided.
    :param list-of-str column_names: names of columns to create
    :param bool only_boolean: True if only want boolean values
                              in the truth table
    Usage example:
      S.createTruthTable(['A', 'B'])
      A = S.getColumnValues('A')  # Trinary object
      B = S.getColumnValues('B')  # Trinary object
      C = A & B | -B
      S.createColumn('C')
      S.setColumnValues('C', C)  # Assign the column value
    """
    columns = []
    for name in column_names:
      columns.append(self._createColumn(name, asis=True))
    # Create the column values
    elements = [False, True]
    if not only_boolean:
      elements.insert(0, None)
    num_lists = len(column_names)
    combinatorics = CombinatoricList(elements)
    results = combinatorics.run(num_lists)
    # Assign the results
    for idx in range(num_lists):
      column = columns[idx]
      self._table.updateColumn(column, results[idx])

  def createTrinary(self, iterable):
    return Trinary(iterable)

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

  def createColumn(self, column_name, index=None):
    """
    Creates a new column, either just to the right of the
    current column (index=None) are at a specific index.
    :param str column_name: name of the column to create
    :param int index: index where the column is to be placed
    :return: column object
    """
    return self._createColumn(column_name, index)

  def deleteColumn(self, column_id):
    """
    Detes an existing a column if it exists.
    :param column_id: either the name of the column or 
                      the 1-based index after the 'row' column
    """
    column = self._getColumn(column_id, validate=False)
    if column is not None:
      _  = self._table.deleteColumn(column)

  def importCSV(self, filepath, column_names=None):
    """
    Imports the specified columns from the csv file.
    Columns that don't exist in the current table are created.
    :param str filepath: full path to file
    :column_names list-of-str: names of a subset of columns in the file
    :return list-of-str: column names imported
    :raises IOError, ValueError:
    """
    df = pd.read_csv(filepath)  # May raise IOError
    df.columns = [Column.cleanName(n) for n in df.columns]
    if column_names is None:
      column_names = df.columns
    error = ""
    imported_names = []
    for name in column_names:
      if not name in df.columns:
        error += "%s is missing column %s\n" % (filepath, name)
        raise ValueError(error)
      else:
        column = self.createColumn(name)
        if column is None:
          import pdb; pdb.set_trace()
        self._table.addCells(column, 
                             np.array(df[name]), 
                             replace=True)
        imported_names.append(column.getName())
    if len(error) > 0:
      raise ValueError(error)
    api_util.writeTableToFile(self._table)
    return imported_names
   

  def param(self, column_id, row_num=1):
    """
    :param str column_name: name of the column referenced
    :param int row_num: row from which the parameter is extracted
    :return: scalar object at the indicate row for the column.
    :raises: ValueError
    """
    column = self._getColumn(column_id)
    values = column.getCells()
    if len(values) < row_num - 1:
      raise ValueError("%s column does not have %d values." 
          % (column_id, row_num))
    return values[row_num-1]


class APIPlugin(APIFormulas):
  """
  Support for running standalone codes
     S = APIPlugin(table_filepath)
     S.initialize()
  """

  def __init__(self, table_filepath):
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
    self._table = api_util.getTableFromFile(self._table_filepath)

  def compareToColumnValues(self, column_name, values):
    """
    Compares the values to those in the column.
    :param str column_name:
    :param object values:
    :return bool: True if successful comparison
    """
    column = self._table.columnFromName(column_name)
    return api_util.compareIterables(column.getCells(), values)

# TODO: Add helper classes for:
#        Columns - representation of a collection of columns
#                  (as a list or dict)
# TODO: Trim unneeded rows of None if cells are deleted
# TODO: verify usage of RowID, ColID, Row
'''
  Implements the table class for SciSheets.
  A table has 1 or more column, and each column has 0 or more cells.
  A table is created with one required column named "row" that indexes
  the rows in the table (starting with 1). The columns in a table
  must have the same number of rows. This is enforced by adjusting
  adjusting column lengths by adding cells with a value of None.
  
A row is identified either by having by the 0 based index of the row.
  All columns in a table should have the same number of rows.
'''


from column import Column
import errors as er
import column as cl
from row import Row
from tableid import RowID, ColID
from util import verifyArgList
import numpy as np

ROW_COLUMN_NAME = "row"
ROW_COLUMN_NUM = 0

class RowDict:
  " Container of values for a row"

  def __init__(self, dic):
    self._row_dic = dic

  def getValues(self):
    return self._row_dic

  def getValue(self, name):
    return self._row_dic[name]

  def setValue(self, name, value):
    self._row_dic[name] = value


#####################################
# Table objects
# When a table is created, the "row" column is created.
#####################################

class ColumnContainer(object):
  # A ColumnContainer can add and delete columns. It has no concept of Rows.
  # It treats columns as independent objects.

  def __init__(self, name):
    self._name = name
    self._columns = []  # array of column objects in table sequence

  def getColumns(self):
    # Returns a list with the column objects in sequence
    return self._columns

  def getColumnFromIndex(self, index):
    # Returns a dictionary with the column object at the index
    return self._columns[index]

  def getColumnFromName(self, name):
    # Finds a column with the specified name or None
    for c in self._columns:
      if c.GetName == name:
        return c
     return None
 
  def getNumColumns(self):
    return len(self._columns)

  def insertColumn(self, column, index=None):
    idx = index
    if idx is None:
      idx = len(self._columns)
    self._columns.(idx, column)


class Table(ColumnContainer):
  # Implements full table functionality.
  # Feature 1: Maintains consistency
  #   between columns as to column lengths 
  #   column names are unique
  # Feature 2: Knows about rows
  #   add rows
  #   delete rows
  #   rows have a name as specified in the row column
  # The primary object for referencing a column is the column object.
  # The primary object for referencing a row is the row index

  def __init__(self, name):
    super(Table, self).__init__(name)
    self._createRowColumn()

  # Data columns are those that have user data. The "row" column is excluded.
  def _getDataColumns(self):
    result = list(self._columns)
    remove_column = self._columns[ROW_COLUMN_NAME]
    result.remove(remove_column)
    return  result

  # TODO: Verify the index 
  def _getRowNameFromIndex(self, index):
    return str(index + 1)

  def _createRowColumn(self):
    col = Column(ROW_COLUMN_NAME)
    self.addColumn(col, adjust=False)

  # TODO: Should this only use RowDict?
  def _validateRow(self, rowl, data_row = False):
    # Validates that the row is consistent with the table
    # Input: rowl - row in list form
    #        data_row - indicates if this is just data or includes
    #                   the row index column (first column)
    # Verify the class of the argument
    if not isinstance(rowl, list):
      raise er.InternalError("In table %s, invalid row format column %s" %
          (self._name, rowl))
    # Verify that the row has the expected length
    if data_row:
      expected_length = self.GetNumDataColumns()
    else:
      expected_length = self.getNumColumns()
    if len(rowl) != expected_length:
      raise er.InternalError("In table %s, row has wrong number cells" %
          self._name)

  def _validateTable(self):
    # Checks that the table is internally consistent
    # The following predicates are considered:
    # Verify that there is at least one column
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    # Verify that all columns have the same number of cells
    num_rows = len(self.getColumnsFromName(ROW_COLUMN_NAME).GetCells())
    for column in self._columns:
      if  column.GetNumCells() != num_rows:
        raise er.InternalError("In Table %s, Column %s differs in its number of rows." %
            (self._name, column.getName()))
     
  def addColumn(self, column, index=None, adjust=True):
    # Adds a column to the table. Ensures uniqueness of column names.
    # Input: column - column object
    #        adjust - adjust column lengths
    if self.getColumnFromName(column.getName())
      raise er.DuplicateColumnName("Table %s already has column %s" %
          (self._name, name))
    self.insertColumn(column, index=index)
    column.setTable(self)
    if adjust:
      self.adjustColumnLengths()
    self._validateTable()

  def insertRow(self, row_dict, index=None):
    # Inserts the row in the desired position in the table
    # Input: row_dict - a RowDict object
    #        index - position in the table where the row is inserted
    # Assigns the value of the ROW_COLUMN
    idx = index
    if idx is None:
      idx = self.getNumRows()
    row_dict.setValue(ROW_COLUMN_NAME, self._getRowName(idx))
    for n in range(self.getNumColumns()):
      column =  self._columns[n]
      name = column.getName()
      if (name in row_dict.getValues().keys())
        column.insertCell(val, idx)
      else:
        column.insertCell(None, idx)

  # TODO: Handle existing row correctly so not adding None
  # TODO: Eliminate need to adjust columns by only adding
  #       Columns with no data
  def updateRow(self, row_dict, index):
    # Updates the row in place
    # Input: row_dict - RowDict representation of row
    #        index - index of row to change
    # Assigns the value of the ROW_COLUMN
    row_dict.setValue(ROW_COLUMN_NAME, self._getRowName(idx))
    for n in range(self.getNumColumns()):
      column =  self._columns[n]
      name = column.getName()
      if (name in row_dict.getValues().keys())
        column.updateCell(val, idx)
      else:
        column.updateCell(None, idx)

  def copy(self):
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._getDataColumns():
      new_column = cl.Column(c.getName())
      new_column.AddCells(c.GetCells().tolist())
      new_table.addColumn(new_column)
    return new_table

  def deleteColumn(self, column)
    # Deletes a column from the table.
    # Input: column - column obj to delete
    column.setTable(None)

  def adjustColumnLengths(self):
    # Ensures that columns are the same length
    if len(self._columns) == 0:
      return
    max_rows = self._columns[ROW_COLUMN_NUM].GetNumCells()
    NONE_ARRAY = np.array([None])
    for col in self._columns.values():
      max_rows = max(max_rows, col.GetNumCells())
    col = self._columns[ROW_COLUMN_NAME]
    if col.GetNumCells() < max_rows:
      col.AddCells(range(col.GetNumCells() + 1, max_rows + 1), adjust=False)
    for col in self._getDataColumns():
      num_rows = col.GetNumCells()
      if num_rows < max_rows:
        added_rows = max_rows - num_rows
        col.AddCells(np.repeat(NONE_ARRAY, added_rows), adjust=False)

# TODO: Trim unneeded rows of None if cells are deleted
'''
  Implements the table class for SciSheets.

  A ColumnContainer has 0 or more Columns. ColumnContainer provides for
  adding, removing, and interrogating its columns. Columns have an
  order within their ColumnContainer. Columns are referenced by their
  object value (the default approach) or by their index within
  the ColumnContainer.

  A Table is a ColumnContainer in which the Columns are maintained
  in a coordinated way.
  a) Columns must have the same number of Cells
  b) Column names must be unique
  c) Columns are referenced by the same index
  A Table has a special Column called the ROW_COLUMN (named "row")
  that is a 1-based index of Cells in Columns. This is called the "row name".
  Table supports the concept of a Row, which is a dictionary in which
  the keys are Column names and the value is the value of the Column's
  Cell for that Row.

  Workflow
    1. Create a Table
    2. Add a Column to the Table
    3. Add Rows to the Table.
    4. Replace Cells in Rows.
'''


from column import Column
import errors as er
import column as cl
from util import verifyArgList
import numpy as np

ROW_COLUMN_NAME = "row"
ROW_COLUMN_NUM = 0

class Row(dict):
  " Container of values for a row"
  pass


#####################################
# Table objects
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
    return self._columns[1:]

  # TODO: Verify the index 
  def _getRowNameFromIndex(self, index):
    return str(index + 1)

  def _createRowColumn(self):
    column = Column(ROW_COLUMN_NAME)
    self.addColumn(column)

  def _adjustColumnLength(self, column):
    # Inserts values of None so that column
    # has the same length as the table
    if len(self._columns) == 0:
      return
    num_rows = self.getNumRows()
    NONE_ARRAY = np.array([None])
    col.addCells(np.repeat(NONE_ARRAY, num_rows))

  def _validateTable(self):
    # Checks that the table is internally consistent
    # Verify that there is at least one column
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    # Verify that all columns have the same number of cells
    num_rows = len(self.getColumnsFromName(ROW_COLUMN_NAME).GetCells())
    for column in self._columns:
      if  column.GetNumCells() != num_rows:
        raise er.InternalError("In Table %s, Column %s differs in its number of rows." % self.getName())
    # Verify that the first Column is the "row" column
    if self._columns[0].name != ROW_COLUMN_NAME:
      raise er.InternalError("In Table %s, first column is not 'row' column", % self.getName())
     
  def addColumn(self, column, index=None)
    # Adds a column to the table. 
    # Ensures uniqueness of column names.
    # Adjusts the Column length to that of the table
    # Input: column - column object
    #        adjust - adjust column lengths
    if self.getColumnFromName(column.getName())
      raise er.DuplicateColumnName("Table %s already has column %s" %
          (self._name, name))
    self.insertColumn(column, index=index)
    column.setTable(self)
    self._adjustColumnLength(column)
    self._validateTable()

  def insertRow(self, row, index=None):
    # Inserts the row in the desired index in the table
    # Input: row - a Row
    #        index - index in the table where the row is inserted
    # Assigns the value of the ROW_COLUMN
    idx = index
    if idx is None:
      idx = self.getNumRows()
    row.[ROW_COLUMN_NAME] =  self._getRowName(idx)
    for n in range(self.getNumColumns()):
      column =  self._columns[n]
      name = column.getName()
      if (name in row.keys())
        column.insertCell(val, idx)
      else:
        column.insertCell(None, idx)

  def updateRow(self, row, index):
    # Updates the row in place. Only changes values
    # that are specified in row.
    # Input: row - Row
    #        index - index of row to change
    # Assigns the value of the ROW_COLUMN
    row.[ROW_COLUMN_NAME] = self._getRowName(idx)
    for n in range(self.getNumColumns()):
      column =  self._columns[n]
      name = column.getName()
      if name in row.keys():
        column.updateCell(val, idx)

  def copy(self):
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._getDataColumns():
      new_column = cl.Column(c.getName())
      new_column.AddCells(c.GetCells().tolist())
      new_table.addColumn(new_column)
    return new_table

  def deleteColumn(self, column):
    # Deletes a column from the table.
    # Input: column - column obj to delete
    column.setTable(None)

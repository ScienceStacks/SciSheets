# TODO: Trim unneeded rows of None if cells are deleted
'''
  Implements the table class for SciSheets.

'''


from column import Column
import errors as er
import column as cl
import numpy as np

NAME_COLUMN_STR = "row"
NAME_COLUMN_IDX = 0

class Row(dict):
  " Container of values for a row"
  pass


#####################################
# Table objects
#####################################

class ColumnContainer(object):
  '''
  A ColumnContainer can add and delete columns. 
  It has no concept of Rows.
  It treats columns as independent objects.
  '''

  def __init__(self, name):
    self._name = name
    self._columns = []  # array of column objects in table sequence

  def deleteColumn(self, column):
    index = self._columns.index(column)
    self.deleteColumnFromIndex(index)

  def deleteColumnFromIndex(self, index):
    del self._columns[index]

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

  def insertColumn(self, column, index=None):
    idx = index
    if idx is None:
      idx = len(self._columns)
    self._columns.insert(idx, column)
 
  def numColumns(self):
    return len(self._columns)


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
    self._createNameColumn()

  # Data columns are those that have user data. The "row" column is excluded.
  def _getDataColumns(self):
    return self._columns[NAME_COLUMN_IDX+1:]

  # TODO: Verify the index 
  def _getRowNameFromIndex(self, index):
    return str(index + 1)

  def _createNameColumn(self):
    column = Column(NAME_COLUMN_STR)
    self.addColumn(column)

  def _adjustColumnLength(self, column):
    # Inserts values of None so that column
    # has the same length as the table
    num_rows = self.numRows()
    NONE_ARRAY = np.array([None])
    column.addCells(np.repeat(NONE_ARRAY, num_rows))

  def _updateNameColumn(self):
    for nn in range(self.numRows):
      name = self._getRowNameFromIndex(nn)
      self._columns[NAME_COLUMN_IDX].updateCell(name, nn)

  def _validateTable(self):
    # Checks that the table is internally consistent
    # Verify that there is at least one column
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    # Verify that all columns have the same number of cells
    num_rows = len(self.getColumnsFromName(NAME_COLUMN_STR).getCells())
    for column in self._columns:
      if  column.numCells() != num_rows:
        raise er.InternalError("In Table %s, Column %s differs in its number of rows." % self.getName())
    # Verify that the first Column is the Name Column
    if self._columns[0].name != NAME_COLUMN_STR:
      raise er.InternalError("In Table %s, first column is not 'row' column" % self.getName())
     
  def addColumn(self, column, index=None):
    # Adds a column to the table. 
    # Adjusts the Column length to that of the table
    # Input: column - column object
    if index is None:
      index = len(self._columns)
    self.insertColumn(column, index=index)
    column.setTable(self)
    self._adjustColumnLength(column)
    self._validateTable()

  def addRow(self, row, index):
    # Input: row - Row to add
    #        index - index where Row is added
    for column in self._columns:
      if row.has_key(column.getName()):
        column.insertCell(row[column.name], index)
      else:
        column.insertCell(None, index)
    self._updateNameColumn()

  def copy(self):
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._getDataColumns():
      new_column = cl.Column(c.getName())
      new_column.addCells(c.getCells())
      new_table.addColumn(new_column)
    return new_table

  def deleteColumn(self, column):
    # Deletes a column from the table.
    # Input: column - column obj to delete
    column.setTable(None)
    self.deleteColumn(column)

  def deleteRow(self, index):
    # Input: index - index of the Row being deleted
    for column in self._columns:
      column.deleteCells([index])
    self._updateNameColumn()

  def getRow(self, index):
    row = Row()
    for c in self._columns:
      row[c.name] = c.getCell[index]
    return row

  def insertRow(self, row, index=None):
    # Inserts the row in the desired index in the table
    # Input: row - a Row
    #        index - index in the table where the row is inserted
    # Assigns the value of the NAME_COLUMN
    idx = index
    if idx is None:
      idx = self.numRows()
    row[NAME_COLUMN_STR] =  self._getRowName(idx)
    for n in range(self.numColumns()):
      column =  self._columns[n]
      name = column.getName()
      if (name in row.keys()):
        column.insertCell(val, idx)
      else:
        column.insertCell(None, idx)

  def moveColumn(self, column, new_index):
    NotYetImplemented

  def numRows(self):
    return self.columns[NAME_COLUMN_IDX].numCells()

  def updateRow(self, row, index):
    # Updates the row in place. Only changes values
    # that are specified in row.
    # Input: row - Row
    #        index - index of row to change
    # Assigns the value of the NAME_COLUMN
    row[NAME_COLUMN_STR] = self._getRowName(idx)
    for n in range(self.numColumns()):
      column =  self._columns[n]
      name = column.getName()
      if name in row.keys():
        column.updateCell(val, idx)

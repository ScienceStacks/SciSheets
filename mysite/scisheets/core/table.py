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

  def columnFromIndex(self, index):
    # Returns the column object at the index
    return self._columns[index]

  def columnFromName(self, name):
    # Finds a column with the specified name or None
    for c in self._columns:
      if c.getName() == name:
        return c
    return None

  def getCell(self, row_index, column_index):
    return self._columns[column_index].getCells()[row_index]

  def getColumns(self):
    # Returns a list with the column objects in sequence
    return self._columns

  def getName(self):
    return self._name

  def insertColumn(self, column, index=None):
    idx = index
    if idx is None:
      idx = len(self._columns)
    self._columns.insert(idx, column)

  def moveColumn(self, column, new_index):
    # Moves the column to the specified index
    # Input: column - column to move
    #        new_index - new index for column
    cur_index = self._columns.index(column)
    del self._columns[cur_index]
    self._columns.insert(new_index, column)
 
  def numColumns(self):
    return len(self._columns)

  def removeColumn(self, column):
    index = self._columns.index(column)
    del self._columns[index]


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
  def _rowNameFromIndex(self, index):
    return str(index + 1)

  def _createNameColumn(self):
    column = Column(NAME_COLUMN_STR)
    self.addColumn(column)

  def _adjustColumnLength(self, column):
    # Inserts values of None so that column
    # has the same length as the table
    NONE_ARRAY = np.array([None])
    adj_rows = self.numRows() - column.numCells()
    if adj_rows > 0:
      column.addCells(np.repeat(NONE_ARRAY, adj_rows))

  def _updateNameColumn(self):
    names = []
    if len(self._columns) > 1:
      for nn in range(self._columns[1].numCells()):
        names.append(self._rowNameFromIndex(nn))
      self._columns[NAME_COLUMN_IDX].addCells(names, replace=True)

  def _validateTable(self):
    # Checks that the table is internally consistent
    # Verify that there is at least one column
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    # Verify that all columns have the same number of cells
    num_rows = len(self.columnFromName(NAME_COLUMN_STR).getCells())
    for column in self._columns:
      if  column.numCells() != num_rows:
        raise er.InternalError("In Table %s, Column %s differs in its number of rows." % 
            (self.getName(), column.getName()))
    # Verify that the first Column is the Name Column
    if self._columns[0].getName() != NAME_COLUMN_STR:
      raise er.InternalError("In Table %s, first column is not 'row' column" % self.getName())
    # Verify that names are unique
    names = []
    for col in self._columns:
      names.append(col.getName())
    if len(names) != len(set(names)):
      raise er.DuplicateColumnName("Duplicate names in Table %s"
          % self.getName())
    # Verify the sequence of row names
    for n in range(self.numRows()):
      expected_row_name = self._rowNameFromIndex(n)
      actual_row_name = self._columns[NAME_COLUMN_IDX].getCells()[n]
      if actual_row_name != expected_row_name:
        raise er.InternalError("In Table %s, invalid row name at index %d: %s"
            % (self.getName(), n, actual_row_name))
     
  def addColumn(self, column, index=None):
    # Adds a column to the table. 
    # Adjusts the Column length to that of the table
    # Input: column - column object
    # Notes: (1) A new column may have either no cells
    #            or the same number as the existing table
    if index is None:
      index = len(self._columns)
    done = False
    # Case 1: NameColumn
    if self.numColumns() == 0 and not done:
      self.insertColumn(column, index=index)
      column.setTable(self)
      done = True
    # Case 2: First column after name column
    if self.numColumns() == 1 and not done:
      self.insertColumn(column, index=index)
      column.setTable(self)
      self._updateNameColumn()
      self._validateTable()
      done = True
    # Case 3: Subsequent columns
    if self.numColumns() > 1 and not done:
      if (column.numCells() != self.numRows() and
          column.numCells() > 0):
        msg = "Invalid number of cells"
        raise er.InvalidColumnStructureForAddToTable(msg)
      else:
        self.insertColumn(column, index=index)
        column.setTable(self)
        self._adjustColumnLength(column)
      self._validateTable()
      done = True

  def addRow(self, row, index=None):
    # Input: row - Row to add
    #        index - index where Row is added
    #                if None, then appended
    if index is None:
      index = self.numRows()
    for column in self._columns:
      if row.has_key(column.getName()):
        column.insertCell(row[column.getName()], index)
      else:
        column.insertCell(None, index)
    self._updateNameColumn()
    self._validateTable()

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
    self.removeColumn(column)

  def deleteRows(self, indicies):
    # Input: indicies - list of rows to delete
    indicies.sort()
    indicies.reverse()
    for column in self._columns:
      column.deleteCells(indicies)
    self._updateNameColumn()

  def getRow(self, index=None):
    # input: index - row desired
    #        if None, then a row of None is returned
    row = Row()
    for c in self._columns:
      if index is None:
        row[c.getName()] = None
      else:
        row[c.getName()] = c.getCells()[index]
    return row

  def insertRow(self, row, index=None):
    # Inserts the row in the desired index in the table
    # Input: row - a Row
    #        index - index in the table where the row is inserted
    # Assigns the value of the NAME_COLUMN
    idx = index
    if idx is None:
      idx = self.numRows()
    for n in range(self.numColumns()):
      column =  self._columns[n]
      name = column.getName()
      if (name in row.keys()):
        column.insertCell(row[name], idx)
      else:
        column.insertCell(None, idx)
    self._updateNameColumn()

  def moveRow(self, index1, index2):
    # Moves the row at index1 to index2
    row = self.getRow(index1)
    self.deleteRows([index1])
    self.insertRow(row, index2)
    self._updateNameColumn()

  def numRows(self):
    return self._columns[NAME_COLUMN_IDX].numCells()

  @staticmethod
  def rowIndexFromName(name):
    return int(name) - 1

  def renameRow(self, rowIndex, proposedName):
    # Renames the row so that it is an integer value
    # that creates the row ordering desired.
    # Inputs: rowIndex - index of the row to change
    #         proposedName - string of a number
    nameColumn = self.getColumns[NAME_COLUMN_IDX]
    names = nameColumn.getCells()
    names[rowIndex] = str(proposedName)
    float_names = names.astype(np.float)
    sortIndex = np.argsort(float_names)
    # ToDo: Use the index toNames method?
    newNames = (np.array(range(len(names))) + 1).astype(str)
    nameColumn.replaceCells(newNames)
    # Update the order of values in each column
    columns = self.getColumns()
    for column in self.getColumns():
      data = column.getCells()
      column.replaceCells(data[sortIndex])

  def updateCell(self, value, row_index, column_index):
    # Changes the value of the identified cell
    # Inputs: value - new value for the cell
    #         row_index - 0-based index of the row
    #         column_index - 0-based index of the column
    column = self.columnFromIndex(column_index)
    column.updateCell(value, row_index)


  def updateRow(self, row, index):
    # Updates the row in place. Only changes values
    # that are specified in row.
    # Input: row - Row
    #        index - index of row to change
    # Assigns the value of the NAME_COLUMN
    row[NAME_COLUMN_STR] = self._rowNameFromIndex(index)
    for n in range(self.numColumns()):
      column =  self._columns[n]
      name = column.getName()
      if name in row.keys():
        column.updateCell(row[name], index)

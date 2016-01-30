# TODO: Trim unneeded rows of None if cells are deleted
'''
  Implements the table class for SciSheets.

'''


from column import Column
import errors as er
import column as cl
import numpy as np
from table_evaluator import TableEvaluator

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

  def indexFromColumn(self, column):
    # Finds the index of the specified column
    return self._columns.index(column)

  def insertColumn(self, column, index=None):
    idx = index
    if idx is None:
      idx = len(self._columns)
    self._columns.insert(idx, column)

  def moveColumn(self, column, new_idx):
    # Moves the column to the specified index
    # Input: column - column to move
    #        new_idx - new index for column
    cur_idx = self.indexFromColumn(column)
    ins_idx = new_idx + 1
    if cur_idx < new_idx:
      ins_idx -= 1
    del self._columns[cur_idx]
    self._columns.insert(ins_idx, column)
 
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

  def _updateNameColumn(self):
    names = []
    if len(self._columns) > 1:
      for nn in range(self._columns[1].numCells()):
        names.append(self._rowNameFromIndex(nn))
      self._columns[NAME_COLUMN_IDX].addCells(names, replace=True)

  # Data columns are those that have user data. The "row" column is excluded.
  def _getDataColumns(self):
    return self._columns[NAME_COLUMN_IDX+1:]

  def getData(self):
    # Returns the data values in an array ordered by column index
    return [c.getCells() for c in self._columns]

  # TODO: Verify the index 
  def _rowNameFromIndex(self, index):
    return str(index + 1)

  # TODO: Verify the index 
  def _rowNamesFromSize(self, size):
    # Inputs: size - number of rows
    # Outputs: result - array of names
    return (np.array(range(size)) + 1).astype(str)

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
    # Case 1: NameColumn
    if self.numColumns() == 0:
      self.insertColumn(column, index=index)
      column.setTable(self)
    # Case 2: First column after name column
    elif self.numColumns() == 1:
      self.insertColumn(column, index=index)
      column.setTable(self)
      self._updateNameColumn()
      self._validateTable()
    # Case 3: Subsequent columns
    else:
      if (column.numCells() != self.numRows() and
          column.numCells() > 0):
        msg = "Invalid number of cells"
        raise er.InvalidColumnStructureForAddToTable(msg)
      else:
        self.insertColumn(column, index=index)
        column.setTable(self)
        self._adjustColumnLength(column)
      self._validateTable()

  def addRow(self, row, ext_index=None):
    # Input: row - Row to add
    #        ext_index - index where Row is added, may be a float
    #                    if None, then appended
    proposed_index = self.numRows()  # Index of new row
    if ext_index is None:
      proposed_name = self._rowNameFromIndex(proposed_index)
    else:
      proposed_name = self._rowNameFromIndex(ext_index)
    for column in self._columns:
      if row.has_key(column.getName()):
        column.insertCell(row[column.getName()])
      else:
        column.insertCell(None)
    last_index = self.numRows() - 1
    self.renameRow(last_index, proposed_name)  # put the row in the right place
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

  def evaluate(self, user_directory=None, import_path=None):
    # Evaluates formulas in the table
    # Output: Error from table evaluation or None
    te = TableEvaluator(self)
    return te.evaluate(user_directory=user_directory, 
                       import_path=import_path)

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

  def renameColumn(self, column, proposed_name):
    # Renames the column, checking for a duplicate
    # Inputs: column - column object
    #         proposed_name - string for name
    # Outputs: Boolean indicating success or failure
    names = [c.getName() for c in self.getColumns()]
    b = all([name != proposed_name for name in names])
    if b:
      column.rename(proposed_name)
    return b

  def renameRow(self, rowIndex, proposed_name):
    # Renames the row so that it is an integer value
    # that creates the row ordering desired.
    # Inputs: rowIndex - index of the row to change
    #         proposed_name - string of a number
    nameColumn = self.getColumns()[NAME_COLUMN_IDX]
    names = nameColumn.getCells()
    names[rowIndex] = str(proposed_name)
    float_names = names.astype(np.float)
    selIndex = np.argsort(float_names)
    newNames = self._rowNamesFromSize(len(names))
    nameColumn.replaceCells(newNames)
    # Update the order of values in each column
    columns = self.getColumns()
    for column in self.getColumns():
      if column.getName() != NAME_COLUMN_STR:
        data = column.getCells()
        column.replaceCells(data[selIndex])

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

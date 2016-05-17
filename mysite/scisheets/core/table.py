'''
  Implements the table class for SciSheets.
'''


from column import Column
from column_container import ColumnContainer
from table_evaluator import TableEvaluator
import errors as er
import column as cl
import numpy as np
import pandas as pd

NAME_COLUMN_STR = "row"
NAME_COLUMN_IDX = 0


class Row(dict):
  """
  Container of values for a row
  """
  pass


# pylint: disable=R0904
class Table(ColumnContainer):
  """
  Implements full table functionality.
  Feature 1: Maintains consistency
    between columns as to column lengths
    column names are unique
  Feature 2: Knows about rows
    add rows
    delete rows
    rows have a name as specified in the row column
  The primary object for referencing a column is the column object.
  The primary object for referencing a row is the row index
  """

  def __init__(self, name):
    super(Table, self).__init__(name)
    self._createNameColumn()
    self.setFilepath(None)

  def d(self):
    return [(c.getName(), c.getCells()) for c in self._columns]

  def f(self):
    return [(c.getName(), c.getFormula()) for c in self._columns]

  def _updateNameColumn(self):
    """
    Changes the cells in the name column to be consecutive ints.
    """
    names = []
    num_cells = self._columns[NAME_COLUMN_IDX + 1].numCells()
    if len(self._columns) > 1:
      for row_num in range(num_cells):
        names.append(Table._rowNameFromIndex(row_num))
      self._columns[NAME_COLUMN_IDX].addCells(names, replace=True)

  # Data columns are those that have user data. The "row" column is excluded.
  def getDataColumns(self):
    """
    Returns the data for a column
    """
    return self._columns[NAME_COLUMN_IDX + 1:]

  def getData(self):
    """
    Returns the data values in an array ordered by column index
    """
    return [c.getCells() for c in self._columns]

  def getFilepath(self):
    return self._filepath

  # TODO: Verify the index
  @staticmethod
  def _rowNameFromIndex(index):
    """
    Create the row name from its index
    """
    return str(index + 1)

  # TODO: Verify the index
  @staticmethod
  def _rowNamesFromSize(size):
    """
    :param size: number of rows
    :return: array of names
    """
    return [str(n) for n in range(1, size+1)]

  def _createNameColumn(self):
    """
    Creates the name column for the table
    """
    column = Column(NAME_COLUMN_STR, asis=True)
    self.addColumn(column)

  def adjustColumnLength(self):
    """
    Inserts values of None or np.nan so that column
        has the same length as the table
    """
    none_array = np.array([None])
    num_rows = self.numRows()
    for column in self._columns:
      adj_rows = num_rows - column.numCells()
      if adj_rows > 0:
        if column.isFloats():
          column.addCells(np.repeat(np.nan, adj_rows))  # pylint:disable=E1101
        else:
          column.addCells(np.repeat(none_array, adj_rows))
    self._updateNameColumn()

  def _validateTable(self):
    """
    Checks that the table is internally consistent
    Verify that there is at least one column
    """
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    # Verify that all columns have the same number of cells
    num_rows = len(self.columnFromName(NAME_COLUMN_STR).getCells())
    for column in self._columns:
      if  column.numCells() != num_rows:
        import pdb; pdb.set_trace()
        msg = "In Table %s, Column %s differs in its number of rows." \
            % (self.getName(), column.getName())
        raise er.InternalError(msg)
    # Verify that the first Column is the Name Column
    if self._columns[0].getName() != NAME_COLUMN_STR:
      msg = "In Table %s, first column is not 'row' column" % self.getName()
      raise er.InternalError(msg)
    # Verify that names are unique
    names = []
    for col in self._columns:
      names.append(col.getName())
    if len(names) != len(set(names)):
      raise er.DuplicateColumnName("Duplicate names in Table %s"
          % self.getName())
    # Verify the sequence of row names
    for nrow in range(self.numRows()):
      expected_row_name = Table._rowNameFromIndex(nrow)
      actual_row_name = self._columns[NAME_COLUMN_IDX].getCells()[nrow]
      if actual_row_name != expected_row_name:
        import pdb; pdb.set_trace()
        msg = "In Table %s, invalid row name at index %d: %s" % \
                (self.getName(), nrow, actual_row_name)
        raise er.InternalError(msg)

  def addCells(self, column, cells, replace=False):
    """
    Adds to the column
    :param Column column:
    :param list cells:
    """
    column.addCells(cells, replace=replace)
    self.adjustColumnLength()
    self._validateTable()

  def addColumn(self, column, index=None):
    """
    Adds a column to the table.
    Adjusts the Column length to that of the table
    :param column: column object
    :param int index: position for the new column
    :return: error text if there is a problem with the column
                    None if no problem
    Notes: (1) A new column may have either no cells
               or the same number as the existing table
    """
    error = None
    # Check for problems with this column
    is_ok = all([c.getName() != column.getName() for c in self._columns])
    if not is_ok:
      error = "**%s is a duplicate name" % column.getName()
      return error
    else:
      error = cl.Column.isPermittedName(column.getName())
      if error is not None:
        return error
    if index is None:
      index = len(self._columns)
    # Handle the different cases of adding a column
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
      self.insertColumn(column, index=index)
      column.setTable(self)
      self.adjustColumnLength()
      self._validateTable()

  def addRow(self, row, ext_index=None):
    """
    :param row: Row to add
    :param ext_index: index where Row is added, may be a float
                       if None, then appended
    """
    # Determine the actual desired name
    if ext_index is None:
      proposed_name = Table._rowNameFromIndex(self.numRows())
    else:
      proposed_name = Table._rowNameFromIndex(ext_index)
    # Assign values to the cells in the Row
    for column in self._columns:
      cur_name = column.getName()
      if cur_name in row:
        column.insertCell(row[cur_name])
      else:
        column.insertCell(None)
    last_index = self.numRows() - 1
    self.renameRow(last_index, proposed_name)  # put the row in the right place
    self._validateTable()

  def copy(self):
    """
    Returns a copy of this object
    """
    new_table = Table(self._name)
    self.setFilepath(None)
    for column in self.getDataColumns():
      new_column = cl.Column(column.getName())
      new_column.addCells(column.getCells())
      new_table.addColumn(new_column)
    return new_table

  def deleteColumn(self, column):
    """
    Deletes a column from the table.
    :param column: column obj to delete
    """
    column.setTable(None)
    self.removeColumn(column)

  def deleteRows(self, indicies):
    """
    Deletes rows
    :param indicies: index of rows to delete
    """
    indicies.sort()
    indicies.reverse()
    for column in self._columns:
      column.deleteCells(indicies)
    self._updateNameColumn()

  def export(self, **kwargs):
    """
    Exports the table to a python program
    :return: error - string from the file export
    """
    table_evaluator = TableEvaluator(self)
    error = table_evaluator.export(**kwargs)
    return error

  def evaluate(self, user_directory=None):
    """
    Evaluates formulas in the table
    :param user_directory: full directory path where user modules
                            are placed
    :return: error from table evaluation or None
    """
    evaluator = TableEvaluator(self)
    return evaluator.evaluate(user_directory=user_directory)

  def getRow(self, index=None):
    """
    :param index: row desired
           if None, then a row of None is returned
    :return: Row object
    """
    row = Row()
    for column in self._columns:
      if index is None:
        if column.isFloats():
          row[column.getName()] = np.nan  # pylint: disable=E1101
        else:
          row[column.getName()] = None
      else:
        row[column.getName()] = column.getCells()[index]
    return row

  def isColumnPresent(self, column_name):
    """
    :param str column_name:
    :return bool: True if column is present
    """
    for column in self._columns:
      if column.getName() == column_name:
        return True
    return False

  def insertRow(self, row, index=None):
    """
    Inserts the row in the desired index in the table and
    assigns the value of the NAME_COLUMN
    :param row: a Row
    :param index: index in the table where the row is inserted
    """
    idx = index
    if idx is None:
      idx = self.numRows()
    for ncol in range(self.numColumns()):
      column = self._columns[ncol]
      name = column.getName()
      if name in row.keys():
        column.insertCell(row[name], idx)
      else:
        column.insertCell(None, idx)
    self._updateNameColumn()

  def migrate(self):
    """
    Handles older objects that lack some properties
    """
    super(Table, self).migrate()

  def moveRow(self, index1, index2):
    """
    Moves the row at index1 to index2
    """
    row = self.getRow(index1)
    self.deleteRows([index1])
    self.insertRow(row, index2)
    self._updateNameColumn()

  def numRows(self):
    """
    Returns the number of rows in the table
    """
    return max([c.numCells() for c in self._columns])

  @staticmethod
  def rowIndexFromName(name):
    """
    Returns the row index for the row name
    """
    return int(name) - 1

  def renameColumn(self, column, proposed_name):
    """
    Renames the column, checking for a duplicate
    :param column: column object
    :param proposed_name: str, proposed name
    :return: Boolean indicating success or failure
    """
    names = [c.getName() for c in self.getColumns()]
    bool_test = all([name != proposed_name for name in names])
    if bool_test:
      column.rename(proposed_name)
    return bool_test

  def renameRow(self, row_index, proposed_name):
    """
    Renames the row so that it is an integer value
    that creates the row ordering desired.
    :param row_index: index of the row to change
    :param proposed_name: string of a number
    """
    name_column = self.getColumns()[NAME_COLUMN_IDX]
    names = name_column.getCells()
    try:
      names[row_index] = str(proposed_name)
    except:
      import pdb; pdb.set_trace()
    float_names = [float(x) for x in names]
    sel_index = np.argsort(float_names)
    new_names = Table._rowNamesFromSize(len(names))
    name_column.replaceCells(new_names)
    # Update the order of values in each column
    for column in self._columns:
      try:
        if column.getName() != NAME_COLUMN_STR:
          data = column.getCells()
          new_data = [data[n] for n in sel_index]
          column.replaceCells(new_data)
      except:
        import pdb; pdb.set_trace()

  def trimRows(self):
    """
    Removes all consequative rows at the end of the table
    that have None values in the data columns
    """
    num_rows = self.numRows()
    row_indxs = range(num_rows)
    row_indxs.sort(reverse=True)
    for index in row_indxs:
      row = self.getRow(index=index)
      del row[NAME_COLUMN_STR]
      delete_row = True
      for name in row.keys():
        column = self.columnFromName(name)
        if column.isFloats():
          if not np.isnan(row[name]):  # pylint: disable=E1101
            delete_row = False
        else:
          if row[name] is not None:
            delete_row = False
      if delete_row:
        self.deleteRows([index])
      else:
        break

  def updateCell(self, value, row_index, column_index):
    """
    Changes the value of the identified cell
    :param value: new value for the cell
    :param row_index: 0-based index of the row
    :param column_index: 0-based index of the column
    """
    column = self.columnFromIndex(column_index)
    column.updateCell(value, row_index)

  def updateColumn(self, column, cells):
    """
    Replaces the cells in the column with those provided
    :param column: column to update
    :param cells: cells to change
    """
    column.addCells(cells, replace=True)
    self.adjustColumnLength()
    self._validateTable()

  def updateRow(self, row, index):
    """
    Updates the row in place. Only changes values
    Assigns the value of the NAME_COLUMN
    that are specified in row.
    :param row: Row
    :param index: index of row to change
    """
    row[NAME_COLUMN_STR] = Table._rowNameFromIndex(index)
    for ncol in range(self.numColumns()):
      column = self._columns[ncol]
      name = column.getName()
      if name in row.keys():
        if name != NAME_COLUMN_STR:
          column.updateCell(row[name], index)

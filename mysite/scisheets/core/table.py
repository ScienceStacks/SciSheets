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


#####################################
# Table objects
# When a table is created, the "row" column is created.
#####################################

class Table(object):

  def __init__(self, name):
    self._name = name
    self._columns = []  # array of column objects in table sequence
    self._createFirstColumn()

  # Data columns are those that have user data. The "row" column is excluded.
  def _getDataColumns(self):
    result = list(self._columns)
    remove_column = self._columns[ROW_COLUMN_NAME]
    result.remove(remove_column)
    return  result

  def _createFirstColumn(self):
    col = Column(ROW_COLUMN_NAME)
    self.AddColumn(col, adjust=False)

  def _findColumnWithName(self, name):
    # Finds a column with the specified name or None
    for c in self._columns:
      if c.GetName == name:
        return c
     return None

  def _validateRow(self, rowl, data_row = False):
    # Validates that the row is consistent with the table
    # Input: rowl - row in list form
    #        data_row - indicates if this is just data or includes
    #                   the row index column (first column)
    if data_row:
      expected_length = self.GetNumDataColumns()
    else:
      expected_length = self.getNumColumns()
    if not isinstance(rowl, list):
      raise er.InternalError("In table %s, invalid row format column %s" %
          (self._name, rowl))
    if len(rowl) != expected_length:
      raise er.InternalError("In table %s, row has wrong number cells" %
          self._name)

  def _validateTable(self):
    # Checks that the table is internally consistent
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    num_rows = len(self._columns[0].GetCells())  # Can't use GetNumRows
    for column in self._columns:
      if  column.GetNumCells() != num_rows:
        raise er.InternalError("In Table %s, Column %s differs in its number of rows." %
            (self._name, column.getName()))
    # Check the column positions
    num_columns = self.getNumColumns()
    if self._column_positions.GetMaxPosition() != num_columns - 1:
      msg = ("Table %s does not have consistent column positions"
            % self.getName())
      raise er.InternalError(msg)
     
  # TODO: Handle adding columns when there is partial data in other columns
  # TODO: Should there be error checking when adding a name column?
  def AddColumn(self, colid, adjust=True):
    # Adds a column to the table. Ensures uniqueness of column names.
    # Input: colid - ColumnID
    #        adjust - adjust column lengths
    if self._findColumnWithName(colid.name)
      raise er.DuplicateColumnName("Table %s already has column %s" %
          (self._name, name))
    # Update table and column state
    column.SetTable(self)
    self._columns.append(column)
    if adjust:
      self.adjustColumnLengths()
    self._validateTable()

  def appendRow(self, row):
    # Appends the row to end of table
    # Input: row - Row object 
    rowl = row.getList()
    rowl[ROW_COLUMN_NUM] = str(self.GetNumRows() + 1)
    for n in range(self.getNumColumns()):
      column =  self._columns[n]
      column.addCells(rowl[n], adjust=False)

  def copy(self):
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._getDataColumns():
      new_column = cl.Column(c.getName())
      new_column.AddCells(c.GetCells().tolist())
      new_table.AddColumn(new_column)
    return new_table

  def deleteColumn(self, colid):
    # Deletes a column from the table.
    # Input: colid - column ID
    self._columns.remove(colid.obj)
    self._validateTable()

  def deleteRows(self, rowids):
    # Deletes the specified rows
    # Input: rowids - list of RowIDs
    index_list = []
    for r in rowids:
      index_list.append(r.index)
    for c in self._columns:
      c.DeleteCells(indicies=index_list, adjust=False)

  def evaluate(self):
    # evaluates the formulas in the table. Evaluation is
    # done in column order.
    raise er.NotYetImplemented("evaluate")

  def getColumns(self):
    # Returns a dictionary with the column objects
    return self._columns

  def GetColumnObject(self, col):
    raise er.InternalError("Deprecated GetColumnObject")

  def GetColumnPosition(self, name):
    return self._column_positions.GetPosition(name)
 
  def getNumColumns(self):
    return len(self._columns)
 
  def GetNumDataColumns(self):
    return len(self._columns) - 1

  def GetNumRows(self):
    if self.getNumColumns() == 0:
      return 0
    column = self._columns.values()[0]
    return column.GetNumCells()
    
  def getName(self):
    return self._name

  def GetRows(self, rowids):
    # Input: rowids - list of RowIDs
    # Returns - dict with k=name, v=array
    result = {}
    for k,v in self._columns.iteritems():
      cells = self._columns[k].GetCells()
      data_list = []
      for i in rowidxs:
        data_list.append(cells[i])
      result[k] = np.array(data_list)
    return result

  def UpdateRow(self, row)
    # Changes the row to the values indicated
    # Input: row - Row object with new values
    rowl = row.getList()
    for n in range(1, self.GetNumDataColumns())
      c = self._columns[n]
      c.UpdateCell(row[ROW_COLUMN_NUM], rowl[n])

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

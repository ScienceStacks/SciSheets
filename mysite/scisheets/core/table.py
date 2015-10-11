# TODO: Add helper classes for:
#        ColId - identifies a column by index or name or object
#                and converts between them
#        Rowidx - identifies a row by index
#        Columns - representation of a collection of columns
#                  (as a list or dict)
#        Row - representation of the cells with the same RowId
#              as a list or a dict        
# TODO: Trim unneeded rows of None if cells are deleted
# TODO: Delete named rows
# TODO: Be consistent with row indexes - always based on 1
'''
  Implements the table class for SciSheets.
  A table has 1 or more column, and each column has 0 or more cells.
  A table is created with one required column named "row" that indexes
  the rows in the table (starting with 1). The columns in a table
  must have the same number of rows. This is enforced by adjusting
  adjusting column lengths by adding cells with a value of None.
  
A row is identified either by having by the 0 based index of the row.
  All columns in a table should have the same number of rows.

  Some notes on variable names:
    Parameters:
      col - either a column object or a column name
      column - column object
      row - either list representation of a row or a
            dict representation of a row
      rowl - list representation of a row
      rowdict - dictionary representation of a row
      rowidx - an int used to (0 based) index into column cells
'''


from column import Column
import errors as er
import column as cl
from helpers import OrderableStrings
import numpy as np

ROW_COLUMN_NAME = "row"

class Table(object):

  def __init__(self, name):
    self._name = name
    self._columns = {}  # key: name, value: object
    self._column_positions = OrderableStrings()
    self._CreateFirstColumn()

  def _GetDataColumns(self):
    result = list(self._columns.values())
    remove_column = self._columns[ROW_COLUMN_NAME]
    result.remove(remove_column)
    return  result

  def _CreateFirstColumn(self):
    col = Column(ROW_COLUMN_NAME)
    self.AddColumn(col, adjust=False)

  def _RowToRowl(self, row):
    # Converts a row that may be represented as a dict (with
    # column name keys) or a list to a list with None for
    # missing entries
    # Input: row - table row either as a list or a dict. Does not
    #              include the "row" column
    # Returns: rowl - table row as a list
    if isinstance(row, list):
      if len(row) != self.GetNumColumns():
        raise er.InternalError("Row %s doesn't match number of columns %d in table %s" %
             (row, self.GetNumColumns(), self.GetName()))
      rowl = row
    elif isinstance(row, dict):
      rowl = []
      for n in range(self.GetNumColumns()):
        columns = [c for c,p in self._column.iteritems() if p == n]
        val = None
        if len(columns) == 1:
          column = columns[0]
          val = row[columns[0].GetName()]
        else:
          raise er.InternalError("Row %s has columns with dupicate names." % row)
        rowl.add(val)
    else:
      raise er.InternalError("Unexpected type %s" % type(row))
    return rowl

  def _ValidateRow(self, rowl, data_row = False):
    # Validates that the row is consistent with the table
    # Input: rowl - row in list form
    #        data_row - indicates if this is just data or includes
    #                   the row index column (first column)
    if data_row:
      expected_length = self.GetNumDataColumns()
    else:
      expected_length = self.GetNumColumns()
    if not isinstance(rowl, list):
      raise er.InternalError("In table %s, invalid row format column %s" %
          (self._name, rowl))
    if len(rowl) != expected_length:
      raise er.InternalError("In table %s, row has wrong number cells" %
          self._name)

  def _ValidateTable(self):
    # Checks that the table is internally consistent
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    num_rows = len(self._columns.values()[0].GetCells())  # Can't use GetNumRows
    for column in self._columns.values():
      if  column.GetNumCells() != num_rows:
        raise er.InternalError("In Table %s, Column %s differs in its number of rows." %
            (self._name, column.GetName()))
    # Check the column positions
    num_columns = self.GetNumColumns()
    if self._column_positions.GetMaxPosition() != num_columns - 1:
      msg = ("Table %s does not have consistent column positions"
            % self.GetName())
      raise er.InternalError(msg)
     
  # TODO: Handle adding columns when there is partial data in other columns
  # TODO: Should there be error checking when adding a name column?
  def AddColumn(self, col, adjust=True):
    # Adds a column to the table. Ensures uniqueness of column names.
    # Input: col - column name (str) or column object
    #        adjust - adjust column lengths
    column = self.GetColumnObject(col)
    name = column.GetName()
    if self._columns.has_key(name):
      raise er.DuplicateColumnName("Table %s already has column %s" %
          (self._name, name))
    # Update the table metadata
    column.SetTable(self)
    self._columns[name] = column
    self._column_positions.Append(name)
    if adjust:
      self.AdjustColumns()
    self._ValidateTable()

  def AddRow(self, row):
    # Adds values to the corresponding columns
    # Input: row - list or dict of values
    rowl = self._RowToRowl(row)
    row_num = self.GetNumRows() + 1
    rowl.insert(0, row_num)
    for p in range(self.GetNumColumns()):
      column =  self.GetColumnObject(p)
      column.AddCells(rowl[p], adjust=False)

  def Copy(self):
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._GetDataColumns():
      new_column = cl.Column(c.GetName())
      new_column.AddCells(c.GetCells().tolist())
      new_table.AddColumn(new_column)
    return new_table

  def DeleteColumn(self, col):
    # Deletes a column from the table.
    # Input: col - column name (str) or column object
    column = self.GetColumnObject(col)
    name = column.GetName()
    column_position = self.GetColumnPosition(column.GetName())
    # Remove from columns dicts
    if not self._columns.has_key(name):
      raise er.ColumnNotFound("Didn't find column %s in table %s" %
          (name, self._name))
    del self._columns[name]
    self._column_positions.Delete(name)
    self._ValidateTable()

  def DeleteRows(self, rowidxs):
    # Deletes the specified rows
    # Input: rowidxs - list of row indicies
    for c in self._columns.values():
      c.DeleteCells(indicies=rowidxs, adjust=False)

  def Evaluate(self):
    # Evaluates the formulas in the table. Evaluation is
    # done in column order.
    raise er.NotYetImplemented("Evaluate")

  def GetColumns(self):
    # Returns a dictionary with the column objects
    return self._columns.values()

  def GetColumnObject(self, col):
    # Input: col - column name (str) or column object or column position
    # Return - column object
    if isinstance(col, cl.Column):
      column = col
    elif isinstance(col, str):
      column = self._columns[col]
    elif isinstance(col, int):
      name = self._column_positions.GetString(col)
      column = self._columns[name]
    else:
      raise InternalError("Invalid type %s" % type(col))
    return column

  def GetColumnPosition(self, name):
    return self._column_positions.GetPosition(name)
 
  def GetNumColumns(self):
    return len(self._columns)
 
  def GetNumDataColumns(self):
    return len(self._columns) - 1

  def GetNumRows(self):
    if self.GetNumColumns() == 0:
      return 0
    column = self._columns.values()[0]
    return column.GetNumCells()
    
  def GetName(self):
    return self._name

  def GetRows(self, rowidxs):
    # Input: rowidxs - rowidxs of rows to be returned
    # Returns - dict with k=name, v=array
    result = {}
    for k,v in self._columns.iteritems():
      cells = self._columns[k].GetCells()
      data_list = []
      for i in rowidxs:
        data_list.append(cells[i])
      result[k] = np.array(data_list)
    return result

  def UpdateRow(self, rowidx, values):
    # Changes the row to the values indicated
    # Input: rowidx - index of row to change
    #        values - list of values corresponding to the columns to be changed
    if len(values) != self.GetNumColumns() - 1:
        raise er.InternalError("Row %d doesn't match number of columns %d in table %s" %
            (rowidx, self.GetNumColumns(), self.GetName()))
    for c in self._columns.values():
      n = self.GetColumnPosition(c.GetName())
      c.UpdateCell(rowidx, values[n])

  def AdjustColumns(self):
    # Ensures that columns are the same length
    if len(self._columns.values()) == 0:
      return
    max_rows = self._columns.values()[0].GetNumCells()
    NONE_ARRAY = np.array([None])
    for col in self._columns.values():
      max_rows = max(max_rows, col.GetNumCells())
    col = self._columns[ROW_COLUMN_NAME]
    if col.GetNumCells() < max_rows:
      col.AddCells(range(col.GetNumCells() + 1, max_rows + 1), adjust=False)
    for col in self._GetDataColumns():
      num_rows = col.GetNumCells()
      if num_rows < max_rows:
        added_rows = max_rows - num_rows
        col.AddCells(np.repeat(NONE_ARRAY, added_rows), adjust=False)

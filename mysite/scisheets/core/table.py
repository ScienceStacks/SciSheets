# TODO: Should there always be a name_column? Default is row number?
# TODO: Add tests for a name column
# TODO: Add helper classes for:
#        ColId - identifies a column by index or name or object
#                and converts between them
#        RowId - identifies a row by index or name
#                and converts between them
#        Columns - representation of a collection of columns
#                  (as a list or dict)
#        Row - representation of the cells with the same RowId
#              as a list or a dict        
# TODO: Trim unneeded rows of None if cells are deleted
'''
  Implements the table class for MVCSheets.
  A table has 0 or more columns. A row is identified either by having
  a special column (name column) or by the 0 based index of the row.
  The name column must be strings, each being unique.
  All columns in a table should have the same number of rows.

  Some notes on names:
    Parameters:
      col - either a column or a column name
      row - either list representation of a row or a
            dict representation of a row
      rowl - list representation of a row
      rowdict - dictionary representation of a row
      rowid - either a name (rowname) or an index (rowidx)
      rowidx - an int used to index into column cells
      rowname - the value of the string in the name column
                that corresponds to the row index
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
    self._name_column = None
    self._CreateFirstColumn()

  def _CreateFirstColumn(self):
    col = Column(ROW_COLUMN_NAME)
    self.AddColumn(col)

  @staticmethod
  def _AddNoneCellsToColumn(column, num):
    # Adds None cells to the end of a column
    # Inputs: column - column object
    #         num - number of cells to add
    column.AddCells([None for n in range(num)])

  def _RowidToRowidx(self, rowids):
    # Obtains the indicies of the rows corresponding to the row names
    # Input: row_names - list of names in the named row
    # Returns - list of row indicies
    if isinstance(rowids[0], int):
      return rowids
    if self._name_column is not None:
      all_names = self._name_column.GetData().tolist()
      all_indicies = range(len(all_names))
    else:
      if len(self._columns) == 0:
        raise er.InternalError("No columns present in table %s" % 
            self._name)
      all_indicies = range(self.GetNumRows())
      all_names = all_indicies
    if row_names is None:
      return all_indicies
    result = [n for n in all_indicies if all_names[n] in set(row_names)]
    return result

  def _RowToRowl(self, row):
    # Converts a row that may be represented as a dict (with
    # column name keys) or a list to a list with None for
    # missing entries
    # Input: row - table row either as a list or a dict
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

  def _ValidateRow(self, rowl):
    # Validates that the row is consistent with the table
    # Input: rowl - row in list form
    if not isinstance(rowl, list):
      raise er.InternalError("In table %s, invalid row format column %s" %
          (self._name, rowl))
    if len(rowl) != self.GetNumColumns():
      raise er.InternalError("In table %s, row has wrong number cells" %
          self._name)

  def _ValidateTable(self):
    # Checks that the table is internally consistent
    if len(self._columns) == 0:
        return
    num_rows = len(self._columns.values()[0].GetCells())
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
  def AddColumn(self, col, name_column=False):
    # Adds a column to the table. Ensures uniqueness of column names.
    # Input: col - column name (str) or column object
    #        name_column - indicates that the column is a key for the table
    column = self.GetColumnObject(col)
    name = column.GetName()
    if self._columns.has_key(name):
      raise er.DuplicateColumnName("Table %s already has column %s" %
          (self._name, name))
    # Ensure that all columns have the same number of rows
    num_missing_cells = self.GetNumRows() - column.GetNumCells()
    if num_missing_cells > 0:
      self._AddNoneCellsToColumn(column, num_missing_cells)
    if num_missing_cells < 0:
      for c in self._columns.values():
        self._AddNoneCellsToColumn(c, -1*num_missing_cells)
    # Update the table metadata
    column.SetTable(self)
    self._columns[name] = column
    if name_column:
      self._name_column = column
    self._column_positions.Append(name)
    self._ValidateTable()

  def AddRow(self, row):
    # Adds values to the corresponding columns
    # Input: row - list or dict of values
    rowl = self._RowToRowl(row)
    for p in range(self.GetNumColumns()):
      column =  self.GetColumnObject(p)
      column.AddCells(rowl[p])

  def Copy(self):
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._columns.values():
      new_column = cl.Column(c.GetName())
      new_column.AddCells(c.GetCells().tolist())
      if self._name_column == c:
        name_column = True
      else:
        name_column = False
      new_table.AddColumn(new_column, name_column=name_column)
    import pdb; pdb.set_trace()
    return new_table

  def DeleteColumn(self, col):
    # Deletes a column from the table.
    # Input: col - column name (str) or column object
    column = self.GetColumnObject(col)
    name = column.GetName()
    column_position = self.GetColumnPosition(column.GetName())
    if self._name_column == column:
      self._name_column = None
    # Remove from columns dicts
    if not self._columns.has_key(name):
      raise er.ColumnNotFound("Didn't find column %s in table %s" %
          (name, self._name))
    del self._columns[name]
    self._column_positions.Delete(name)
    self._ValidateTable()

  def DeleteRows(self, rowids):
    # Deletes the specified rows
    # Input: rowids - list of row names or indicies
    rowidxs = self._RowidToRowidx(rowids)
    for c in self._columns.values():
      c.DeleteCells(indicies=rowidxs)

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

  def GetNumRows(self):
    if self.GetNumColumns() == 0:
      return 0
    column = self._columns.values()[0]
    return column.GetNumCells()
    
  def GetName(self):
    return self._name

  def GetRows(self, row_names=None):
    # Input: row_names - names of rows to be returned
    # Returns - dict with k=name, v=array
    result = {}
    if row_names is None:
      indicies = range(self.GetNumRows())
    else:
      indicies = self._RowidToRowidx(row_names)
    for k,v in self._columns.iteritems():
      cells = self._columns[k].GetCells()
      data_list = []
      for i in indicies:
        data_list.append(cells[i])
      result[k] = np.array(data_list)
    return result

  def UpdateRow(self, rowid, rowl):
    # Changes the row to the values indicated
    # Input: rowid - row name (if name column is not None) or index
    #        rowl - list of values corresponding to the columns to be changed
    indicies = self._RowidToRowidx([rowid])
    if len(indicies) != 1:
      raise er.InternalError("Expected exactly one row")
    if len(indicies) > 1:
      rowidx = indicies[0]
      keys = self._columns.keys()
      for c in self._columns.values():
        n = self.GetColumnPosition(c.GetName())
        c.UpdateCell(rowidx, rowl[n])

  def AdjustColumns(self):
    # Ensures that columns are the same length
    max_rows = self._columns.values()[0].GetNumCells()
    NONE_ARRAY = np.array([None])
    for col in self._columns.values():
      max_rows = max(max_rows, col.GetNumCells())
    for col in self._columns.values():
      num_rows = col.GetNumCells()
      if num_rows < max_rows:
        added_rows = max_rows - num_rows
        col.AddCells(np.repeat(NONE_ARRAY, added_rows))

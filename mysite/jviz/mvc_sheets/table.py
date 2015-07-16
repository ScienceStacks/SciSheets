'''
  Implements the table class for MVCSheets.
  A table has 0 or more columns. A row is identified either by having
  a special column (name column) or by the 0 based index of the row.

  Some notes on names:
    Parameters:
      col - either a column or a column name
      rowid - either a row name or the index of the row
'''


import exceptions as e
import column as c
from numpy import array


# TODO: Should there always be a name_column? Default is row number?
class Table(object):

  def __init__(self, name)
    self._name = name
    self._columns = {}  # key: name, value: object
    self._name_column = None

  @staticmethod
  def _GetColumnObject(col):
    # Input: col - column name (str) or column object
    # Return - column object
    if isinstance(col, c.Column):
      column = col
    else:
      column = c.Column(name)
    return column

  def _GetRowIndicies(self, row_names):
    # Obtains the indicies of the rows corresponding to the row names
    # Input: row_names - list of names in the named_row, or integer indicies
    # Returns - list of row indicies
    if self._name_column is not None:
      all_names = self._name_column.GetData().tolist()
      all_indicies = range(len(all_names))
    else:
      if len(self._columns) == 0:
        raise e.InternalError("No columns present in table %s" % 
            self._name)
      all_indicies = range(len(self._columns.values[0])
      all_names = all_indicies
    if row_names is None:
      return all_indicies
    result = [n for n in all_indicies if all_names[n] in set(row_names)]
    return result

  def _ValidateTable(self):
    # Checks that the table is internally consistent
    keys = self._columns.keys()
    values = self._columns.values()
    num_rows = len(values[0])
    for n in range(len(values)):
      if len(values[n]) != num_rows:
        raise e.InternalError("In Table %s, Row %d has length %d. Expected %d." %
            (self._name, n, len(values[n]), num_rows))
    
    

  # TODO: Handle adding columns when there is partial data in other columns
  # TODO: Should there be error checking when adding a name column?
  def AddColumn(self, col, name_column=False):
    # Adds a column to the table. Ensures uniqueness of column names.
    # Input: col - column name (str) or column object
    #        name_column - indicates that the column is a key for the table
    column = self._GetColumnObject(col)
    name = column.GetTableName()
    if self._columns.has_key(name):
      raise e.DuplicateColumnName("Table %s already has column %s" %
          (self._name, name))
    column.SetTable(self)
    self._columns[name] = column
    if name_column:
      self._name_column = column

  def AddRow(self, values):
    # Adds values to the corresponding columns
    # Input: values - list of values
    raise e.NotYetImplemented("AddRow")

  def Copy(self)
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._columns.values():
      new_column = Column(c.GetTableName())
      if self._name_column == c:
        name_column = True
      else:
        name_column = False
      new_table.AddColumn(new_column, name_column=name_column)
    return new_table
    
    raise e.NotYetImplemented("Copy")

  def DelColumn(self, col):
    # Deletes a column from the table.
    # Input: col - column name (str) or column object
    column = self._GetColumnObject(col)
    if self._name_column == column:
      self._name_column = None
    # Remove from columns dict
    if self._columns.has_key(name):
      del self._columns[name]
    else:
      raise e.ColumnNotFound("Didn't find column %s in table %s" %
          (name, self._name))

  def DelRows(self, rowids):
    # Deletes the specified rows
    # Input: rowids - list of row names or indicies
    raise e.NotYetImplemented("DelRow")

  def Evaluate(self):
    # Evaluates the formulas in the table. Evaluation is
    # done in column order.
    raise e.NotYetImplemented("Evaluate")

  def GetColumns(self):
    # Returns a dictionary with the column objects
    return self._columns
    
  def GetTableName(self):
    return self._name

  def GetRows(self, row_names=None):
    # Input: row_names - names of rows to be returned
    # Returns - dict with k=name, v=array
    result = {}
    indicies = self._GetRowIndicies(row_names)
    for k,v in self._columns:
      cells = self._columns.GetCells()
      data_list = []
      for i in indicies:
        data_list.append(cells[i])
      result[k] = array(data_list)
    return result

  def UpdateRow(self, rowid, row_values):
    # Changes the row to the values indicated
    # Input: rowid - row name (if name column is not None) or index
    #        row_values - list of values corresponding to the columns to be changed
    indicies = self._GetRowIndicies(rowid)
    if len(indicies) != 1:
      raise e.InternalError("Expected exactly one row")
    index = indicies[0]
    keys = self._columns.keys()
    values = self._columns.values()
    for n in range(len(self._columns)):
      column_values = value[n]
      new_column_values[index] = row_values[n]
      self._columns[keys[n]] = new_column_values

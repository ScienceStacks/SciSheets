'''
  Implements the table class for MVCSheets.
'''


import exceptions as e
import column as c
from numpy import array


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

  def _SelRows(self, row_names, data):
    # Selects the rows from the array that correspond to the desired
    # row names.
    # Input: row_names - list of rows to select
    #        data - array of data to select
    # Returns - result, an array
    if row_names is None:
      return data
    data_list = data.tolist()
    selected_data = []
    for n in range(len(row_names)):
      if self._name_column[n] is in set(row_names):
        selected_data.append(data_list[n])
    return array(selected_data)

  # TODO: Handle adding columns when there is partial data in other columns
  # TODO: Should there be error checking when adding a name column?
  def AddColumn(self, col, name_column=False):
    # Adds a column to the table. Ensures uniqueness of column names.
    # Input: col - column name (str) or column object
    #        name_column - indicates that the column is a key for the table
    column = self._GetColumnObject(col)
    name = column.GetName()
    if self._columns.has_key(name):
      raise e.DuplicateColumnName("Table %s already has column %s" %
          (self._name, name))
    column.SetTable(self)
    self._columns[name] = column
    if name_column:
      self._name_column = column

  def Copy(self)
    # Returns a copy of this object
    new_table = Table(self._name)
    for c in self._columns.values():
      new_column = Column(c.GetName())
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

  def Evaluate(self):
    # Evaluates the formulas in the table. Evaluation is
    # done in column order.
    raise e.NotYetImplemented("Evaluate")

  def GetColumns(self):
    # Returns a dictionary with the column objects
    return self._columns
    
  def GetName(self):
    return self._name

  def GetRows(self, row_names=None):
    # Input: row_names - names of rows to be returned
    # Returns - dict with k=name, v=array
    result = {}
    if row_name is not None and self._name_column is None:
      raise e.NoNameRow(self._name)
    for k,v in self._columns:
      result[k] = self._SelRows(row_names, self._columns.GetCells())
    return result

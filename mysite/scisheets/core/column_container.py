'''
  Implements the ColumnContainer.
'''


from column import Column
import errors as er
import column as cl


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
    """
    :return: column object at the index
    """
    return self._columns[index]

  def columnFromName(self, name):
    """
    Finds a column with the specified name or None
    :param name: name of the column
    :return: column - column object or None if not found
    """
    for  column in self._columns:
      if  column.getName() == name:
        return  column
    return None

  def getCell(self, row_index, column_index):
    """
    :return: the numpy array of the cells in the column
    """
    return self._columns[column_index].getCells()[row_index]

  def getColumnNames(self):
    """
    :return list-of-str:
    """
    return [c.getName() for c in self._columns]

  def getColumns(self):
    """
    :return: list with the column objects in sequence
    """
    return self._columns

  def getName(self):
    """
    :return: the table name
    """
    return self._name

  def indexFromColumn(self, column):
    """
    Finds the index of the specified column
    :param column: column object
    """
    return self._columns.index(column)

  def insertColumn(self, column, index=None):
    """
    Inserts the column after the specified column index
    :param column: object
    :param index: column index
    """
    idx = index
    if idx is None:
      idx = len(self._columns)
    self._columns.insert(idx, column)

  def migrate(self):
    """
    Handles older objects that lack some properties
    """
    pass

  def moveColumn(self, column, new_idx):
    """
    Moves the column to the specified index
    :param column: column to move
    :param new_idx: new index for column
    """
    cur_idx = self.indexFromColumn(column)
    ins_idx = new_idx + 1
    if cur_idx < new_idx:
      ins_idx -= 1
    del self._columns[cur_idx]
    self._columns.insert(ins_idx, column)

  def numColumns(self):
    """
    Returns the number of columns in the table
    """
    return len(self._columns)

  def removeColumn(self, column):
    """
    Removes the column object from the table
    """
    index = self._columns.index(column)
    del self._columns[index]

  def setFilepath(self, filepath):
    # Path to the backing store for the Table
    self._filepath = filepath

  def setName(self, name):
    """
    :param name: new table name
    :return: error string if invalid name, else None
    """
    try:
      _ = compile(name, "string", "eval")
      error = None
      self._name = name
    except SyntaxError as err:
      error = str(err)
    return error

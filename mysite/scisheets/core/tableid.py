'''
 Entity identifier classes.
 These classes provide a way of representing and accessing
 SciSheet entities - Columns, Rows
'''

import errors as er

class RowID(object):
''' Identify a row in the table. '''

  def __init__(self, table, index=None, row_num= None):
    # The constructor must specify at least one of index and row_num
    # Input: table - table being referenced
    #        index - 0 based index of the row
    #        row_num - 1 based index of the row as a string 
    #                  (as appears in the "row" column)
    self._table = table
    self._index = index
    self._row_num = index
    verifyArgList(self._index, self._row_num)
    self._setup(self)

  def _setup(self):
    if self._row_num is not None:
      try:
        self._index = int(self._row_num) - 1
      except:
        raise er.InternalError("%s is not an int" % row_num)
    if self._index is not None:
      self._row_num = str(index + 1)

  def getIndex(self):
    return self._index

  def getRowNum(self):
    return self._row_num


class ColID(object):
''' Identify a column in the table. '''

  def __init__(self, table, index=None, position=None, name=None, obj=None):
    # The constructor must specify at least one of index, name, obj
    # Input: table - table being referenced (required)
    #        index - 0 based index of the column
    #        position - 1 based index of column that refers to its external view
    #        name - column name
    #        obj - column object
    # Exactly one of the optional arguments can be specified
    self._table = table
    self._index = index
    self._position = index
    self._name = name
    self._obj = obj
    verifyArgList(self._index, self._position, self._name, self._obj)
    self._setup()

  def getPosition(self):
    return self._position

  def getIndex(self):
    return self._index

  def getName(self):
    return self._name

  def getObj(self):
    return self._obj

  def _setup(self):
    if self._index is not None:
      self._setupFromIndex()
    if self._position is not None:
      self._setupFromPosition()
    if self._name is not None:
      self._setupFromName()
    if self._obj is not None:
      self._setupFromObj()

  def _assignPosition(self):
    self._position = self._index + 1

  def _setupFromName(self):
    # Input: name - column name
    columns = self._table.getColumns()
    for n in range(len(columns)):
      if columns[n].getName() == name:
        self._obj = c
        self._index = n
        self._assignPosition()
        return
    raise er.InternalError("Could not find column %s" % name)

  def _setupFromIndex(self):
    # Input: index - column index
    self._assignPosition()
    self._obj = self._table.getColumns()[index]
    self._name = self._obj.getName()

  def _setupFromObj(self):
    columns = self._table.getColumns()
    for n in range(len(columns)):
      if columns[n] == self._obj:
        self._index = n
        self._assignPosition()
        self._name = columns[n].GetName()
        return
    raise er.InternalError("Could not find column.")

  def _setupFromPosition(self)
    self._index = self._position - 1
    self._setupFromIndex(self._index)

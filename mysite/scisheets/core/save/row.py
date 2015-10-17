'''Row access.'''

#####################################
# Row object. Representation of a row.
# List representation has a value for each column (with None set for missing values)
#####################################
class Row(object):

  def __init__(self, table, row_list=None, row_dict=None):
  # Representation of a row in a table
  # Input: table - table in which the row resides
  #        row_list - row represented as a list of values in sequence
  #        row_dict - row represented as a dictionary with the key
  #                   being the colid and the value being the column value.
  #                   This is a sparse representation
  # Notes: Exactly one of row_list and row_dict must be specified.
  self._table = table
  self._list = row_list
  self._dict = row_dict
  verifyArgList(self._list, self._dict)
  if self._list is None:
    self._calcListFromDict()
  if self._dict is None:
    self._calcDictFromList()

  def _calcListFromDict(self):
    self._list = []
    for n in self._table.getNumColumns():
      self._list.append(None)
    for name in self._dict.keys():
      colid = ColID(self._table, name=name)
      idx = colid.getIndex()
      self._list[idx] = self._dict[name]

  def _calcDictFromList(self):
    self._dict = {}
    for col in self._table.getColumns():
      colid = ColID(self, obj=col)
      self._dict[col.getName()] = self._list[colid.getIndex()]

  def getList(self):
    return self._list

  def getDict(self):
    return self._dict

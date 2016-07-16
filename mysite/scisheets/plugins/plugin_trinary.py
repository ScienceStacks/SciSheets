"""
Code to create and manipulation trinary truth tables
"""

from scisheets.core.helpers.trinary import Trinary

def createTruthTable(s, column_names, only_boolean=False):
  """
  Creates a truth table with all combinations of Boolean
  values for the number of columns provided.
  :param list-of-str column_names: names of columns to create
  :param bool only_boolean: True if only want boolean values
                            in the truth table
  Usage example:
    S.createTruthTable(['A', 'B'])
    A = S.getColumnValue('A')  # Trinary object
    B = S.getColumnValue('B')  # Trinary object
    C = A & B | -B
    S.createColumn('C')
    S.setColumnValue('C', C)  # Assign the column value
  """
  columns = []
  for name in column_names:
    # TODO: Don't use internal method
    columns.append(s.createColumn(name, asis=True))
  # Create the column values
  elements = [False, True]
  if not only_boolean:
    elements.insert(0, None)
  num_lists = len(column_names)
  combinatorics = CombinatoricList(elements)
  results = combinatorics.run(num_lists)
  # Assign the results
  for idx in range(num_lists):
    column = columns[idx]
    self._table.updateColumn(column, results[idx])

def createTrinary(iterable):
  return Trinary(iterable)

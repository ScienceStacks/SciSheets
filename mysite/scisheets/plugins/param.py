"""
Converts a value in a column to a scalar.
"""

def param(s, column_id, row_num=1):
  """
  :param API s: API object
  :param str column_name: name of the column referenced
  :param int row_num: row from which the parameter is extracted
  :return: scalar object at the indicate row for the column.
  :raises: ValueError
  """
  column = s.getColumn(column_id)
  values = column.getCells()
  if len(values) < row_num - 1:
    raise ValueError("%s column does not have %d values." 
        % (column_id, row_num))
  return values[row_num-1]

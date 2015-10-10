'''
  Extends the Table class to display a table and respond to UI events
'''


from ..core.table import Table
from numpy import array


class UITable(Table):

  def _Make_MSON_string(column_names, data):
  # Creates a string that javascript parses into JSON
  # Input: column_names - list of names of the data columns
  #        data - list of columns of data
  # Output: result - JSON parseable string
  number_of_columns = len(column_names)
  if len(data) > 0:
    number_of_rows = len(data[0])
  else:
    number_of_rows = 0
  result = "'["
  for r in range(number_of_rows):
    result += "{"
    for c in range(number_of_columns):
      result += ('"' + column_names[c] + '": ' + 
          '"' + str(data[c][r]) + '"')
      if c != number_of_columns - 1:
        result += ","
      else:
        result += "}"
    if r < number_of_rows -1:
      result += ","
  result += "]'"
  return result

  def GetContext(self):
    # Returns the context required to render the table using
    # the scitable_data.html template
    # Output: result - a dictionary with the value specifications
    result = {}
    result['table_caption'] = self._name
    column_names = []
    columns = self.GetColumns()
    for column in columns
      column_names.append(column.GetName())
    result['column_names'] = column_names
    result['final_column_name'] = column_names[-1]
    data = []
    for column in columns:
      data.append(column.GetCells())
    result['data'] = self._Make_JSON_string(data)
    return result

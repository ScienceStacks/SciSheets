'''
  Extends the Table class to display a table and respond to UI events
'''

from django.shortcuts import render
from django.template.loader import get_template
from numpy import array
from ..core.table import Table


def makeJSONStr(column_names, data):
  # Creates a string that javascript parses into JSON in
  # the format expected by YUI datatable
  # Input: column_names - list of variables
  #        data - list of array data
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

def getContext(table_name, column_names, data):
  # Returns the context required to render the table using
  # the scitable_data.html template
  # Output: result - a dictionary with the value specifications
  result = {}
  result['table_caption'] = self._name
  column_names = []
  columns = self.GetColumns()
  for column in columns:
    column_names.append(column.GetName())
  result['column_names'] = column_names
  result['final_column_name'] = column_names[-1]
  data = []
  for column in columns:
    data.append(column.GetCells())
  result['data'] = self._Make_JSON_string(data)
  return result

class UITable(Table):
  ''' 
      Extends the Table class to provide rendering of the Table as
      a YUI DataTable.
  '''
  
  def render(self, table_id="scitable"):
    # Input: table_id - how the table is identified in the HTML
    # Output: html rendering of the Table
    column_names = [c.getName() for c in self._columns]
    column_data = [c.getCells().tolist() for c in self._columns]
    data = makeJSONStr(column_names, column_data)
    ctx_dict = {'column_names': column_names,
                'final_column_name': column_names[-1],
                'table_caption': self.getName(),
                'table_id': table_id,
                'data': data,
               }
    html = get_template('scitable.html').render(ctx_dict)
    return html

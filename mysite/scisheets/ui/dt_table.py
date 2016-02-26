'''
  YUI DataTable specific rendering of tables
'''

from django.shortcuts import render
from django.template.loader import get_template
from ui_table import UITable
from mysite import settings as st


def makeJSON(column_names, data):
  """
  Creates a valid JSON for javascript in
  the format expected by YUI datatable
  Input: column_names - list of variables
         data - list of array data or a list of values
  Output: result - JSON as an array
  """
  number_of_columns = len(column_names)
  if len(data) > 0:
    if isinstance(data[0], list):
      number_of_rows = len(data[0])
    else:
      number_of_rows = 1
  else:
    number_of_rows = 0
  result = "["
  for r in range(number_of_rows):
    result += "{"
    for c in range(number_of_columns):
      if isinstance(data[c], list):
        if len(data[c]) - 1 < r:
          item = ""  # Handle ragged columns
        else:
          item = data[c][r]
      else:
        item = data[c]
      if item is None:
        value = ""
      else:
        value = str(item)
      result += '"' + column_names[c] + '": ' + '`' + value + '`'
      if c != number_of_columns - 1:
        result += ","
      else:
        result += "}"
    if r < number_of_rows -1:
      result += ","
  result += "]"
  return result



class DTTable(UITable):
  """
  Does rendersing specific to YUI DataTable
  """

  @staticmethod
  def _formatStringForJS(in_string):
    """
    Formats the string so that it can be assigned as a value 
    in javascript
    Input: in_string - string to format
    Output: formated string
    """
    return '`%s`' % str(in_string)

  def render(self, table_id="scitable", table_file=""):
    """
    Input: table_id - how the table is identified in the HTML
    Output: html rendering of the Table
    """
    column_names = [c.getName() for c in self._columns]
    column_data = [c.getCells().tolist() for c in self._columns]
    raw_formulas = [c.getFormula() for c in self._columns]
    formulas = []
    for ff in raw_formulas:
      if ff is None or (ff == "None"):
        formulas.append("''")
      else:
        formulas.append(DTTable._formatStringForJS(ff))
    formula_dict = {}
    for nn in range(len(column_names)):
      formula_dict[column_names[nn]] = formulas[nn]
    data = makeJSON(column_names, column_data)
    indicies = range(len(column_names))
    ctx_dict = {'column_names': column_names,
                'final_column_name': column_names[-1],
                'table_caption': self.getName(),
                'table_id': table_id,
                'data': data,
                'formula_dict': formula_dict,
                'num_cols': len(column_names),
                'count': 1,
                'table_file': DTTable._formatStringForJS(table_file),
               }
    html = get_template('scitable.html').render(ctx_dict)
    return html

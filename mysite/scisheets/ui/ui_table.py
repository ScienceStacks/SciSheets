'''
  Extends the Table class to display a table and respond to UI events
'''

from django.shortcuts import render
from django.template.loader import get_template
from ..core.table import Table
from ..core.column import Column
from mysite.helpers import util as ut
import numpy as np
import random


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


class UITable(Table):
  ''' 
      Extends the Table class to provide rendering of the Table as
      a YUI DataTable.
  '''

  @classmethod
  def createRandomTable(cls, name, nrow, ncol, ncolstr=0,
        low_int=0, hi_int=100):
    # Creates a table with random integers as values
    # Input: name - name of the table
    #        nrow - number of rows
    #        ncol - number of columns
    #        ncolstr - number of columns with strings
    #        low_int - smallest integer
    #        hi_int - largest integer
    ncol = int(ncol)
    nrow = int(nrow)
    table = UITable(name)
    ncolstr = min(ncol, ncolstr)
    ncolint = ncol - ncolstr
    c_list = range(ncol)
    random.shuffle(c_list)
    for n in range(ncol):
      column = Column("Col-" + str(n))
      if c_list[n] < ncolint - 1:
        values = np.random.randint(low_int, hi_int, nrow)
      else:
        values = ut.randomWords(nrow)
      column.addCells(values)
      table.addColumn(column)
    return table

  def processCommand(self, cmd_dict):
    # Processes a UI request for the Table.
    # Input: cmd_dict - dictionary with the keys
    #          target - type of table object targeted: Cell, Column, Row
    #          command - command issued
    #          table_name - name of the table
    #          column_index - 0 based index
    #          row_index - 0 based index of row
    #          value - value assigned
    # Output: response - Dictionary with response
    #            data: data returned
    #            success: True/False
    response = {'data': None, 'success': False}
    # Cells
    if cmd_dict["target"] == "Cell":
      if cmd_dict["command"] == "Update":
        self.updateCell(cmd_dict["value"], 
                        cmd_dict["row_index"], 
                        cmd_dict["column_index"])
        response["data"] = "OK"
        response["success"] = True
    if cmd_dict["target"] == "Column":
      if cmd_dict['command'] == "Delete":
        column = self.columnFromIndex(cmd_dict["column_index"])
        self.deleteColumn(column)
        num_cols = self.numColumns()
        response["data"] = "OK"
        response["success"] = True
    if not response["success"]:
      NotYetImplemented
    return response
  
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

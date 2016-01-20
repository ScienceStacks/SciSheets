'''
  Extends the Table class to display a table and respond to UI events
'''

from django.shortcuts import render
from django.template.loader import get_template
from ..core.table import Table
from ..core.column import Column
from ..core.errors import NotYetImplemented
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
      if c_list[n] <= ncolint - 1:
        values = np.random.randint(low_int, hi_int, nrow)
        values_ext = values.tolist()
      else:
        values_ext = ut.randomWords(nrow)
      #values_ext.append(None)
      column.addCells(np.array(values_ext))
      table.addColumn(column)
    return table

  @staticmethod
  def _createResponse(success=False):
    # Returns a response of the desired type
    # Input: success - successful response if true,
    #                  unsuccessful response if false
    # Output: response
    if success:
      response = {'data': "OK", 'success': True}
    else:
      response = {'data': None, 'success': False}
    return response
  

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
    response = self._createResponse(success=False)
    # Table
    # Cells
    target = cmd_dict["target"]
    command = cmd_dict["command"]
    if target == "Cell":
      if command == "Update":
        self.updateCell(cmd_dict["value"], 
                        cmd_dict["row_index"], 
                        cmd_dict["column_index"])
      else:
        msg = "Unimplemented %s command: %s." % (target, command)
        raise NotYetImplemented(msg)
    elif target == "Column":
      column = self.columnFromIndex(cmd_dict["column_index"])
      if (command == "Append") or (command == "Insert"):
        name = cmd_dict["args"][0]
        new_column = Column(name)
        increment = 0
        if command == "Append":
          increment = 1
        new_column_index = cmd_dict["column_index"] + increment
        self.addColumn(new_column, new_column_index)
      elif command == "Delete":
        self.deleteColumn(column)
      elif command == "Rename":
        column.rename(cmd_dict["args"][0])
      else:
        msg = "Unimplemented %s command: %s." % (target, command)
        raise NotYetImplemented(msg)
    elif target == "Row":
      row_index = cmd_dict['row_index']
      if command == "Move":
        new_name = cmd_dict["args"][0]
        self.renameRow(row_index, new_name)
      elif command == "Delete":
        self.deleteRows([row_index])
      elif command == "Insert":
        row = self.getRow()
        self.addRow(row, row_index - 0.1)  # Add a new row before 
      elif command == "Append":
        row = self.getRow()
        self.addRow(row, row_index + 0.1)  # Add a new row after
      else:
        msg = "Unimplemented %s command: %s." % (target, command)
        raise NotYetImplemented(msg)
    else:
        msg = "Unimplemented %s." % target
        raise NotYetImplemented(msg)
    response = self._createResponse(success=True)
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

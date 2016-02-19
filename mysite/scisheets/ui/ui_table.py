'''
  Extends the Table class to display a table and respond to UI events
'''

from django.shortcuts import render
from django.template.loader import get_template
from ..core.table import Table
from ..core.column import Column
from ..core.errors import NotYetImplemented
from mysite.helpers import util as ut
from mysite import settings as st
import collections
import numpy as np
import os
import random
import re


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


class UITable(Table):
  """
  Extends the Table class to provide rendering of the Table as
  a YUI DataTable.
  """

  @classmethod
  def createRandomTable(cls, name, nrow, ncol, ncolstr=0,
        low_int=0, hi_int=100):
    """
    Creates a table with random integers as values
    Input: name - name of the table
           nrow - number of rows
           ncol - number of columns
           ncolstr - number of columns with strings
           low_int - smallest integer
           hi_int - largest integer
    """
    ncol = int(ncol)
    nrow = int(nrow)
    table = UITable(name)
    ncolstr = min(ncol, ncolstr)
    ncolint = ncol - ncolstr
    c_list = range(ncol)
    random.shuffle(c_list)
    for n in range(ncol):
      column = Column("Col_" + str(n))
      if c_list[n] <= ncolint - 1:
        values = np.random.randint(low_int, hi_int, nrow)
        values_ext = values.tolist()
      else:
        values_ext = ut.randomWords(nrow)
      #values_ext.append(None)
      column.addCells(np.array(values_ext))
      table.addColumn(column)
    return table

  def _createResponse(self, error):
    # Returns a response of the desired type
    # Input: error - result of processing a command
    #                (may be None)
    # Output: response
    if error is None:
      new_error = self.evaluate(user_directory=st.SCISHEETS_USER_PYDIR,
                                import_path=st.SCISHEETS_USER_PYPATH)
    else:
      new_error = error
    if new_error is None:
      response = {'data': "OK", 'success': True}
    else:
      response = {'data': str(error), 'success': False}
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
    target = cmd_dict["target"]
    if target == "Cell":
      response = self._cellCommand(cmd_dict)
    elif target == "Column":
      response = self._columnCommand(cmd_dict)
    elif target == "Row":
      response = self._rowCommand(cmd_dict)
    elif target == "Table":
      response = self._tableCommand(cmd_dict)
    else:
        msg = "Unimplemented %s." % target
        raise NotYetImplemented(msg)
    return response

  def _extractListFromString(self, list_as_str):
    # TODO: Test
    # Input: list_as_str - comma or blank separated tokens
    # Output: result - list of the separated tokens
    #         error - error string or None
    result = re.findall(r'(?ms)\W*(\w+)', list_as_str)
    for name in result:
      if self.columnFromName(name) is None:
        error = "Unknown column name: %s" % name
        return result, error
    return result, None

  def _listTableFiles(self):
    # TODO: Tests
    # Output: returns as response that contains the list of table files in data
    LENSFX = len(".pcl")
    file_list = [ff[:-LENSFX] for ff in os.listdir(st.BASE_DIR) 
                 if ff[-LENSFX:] == '.pcl']
    return {'data': file_list, 'success': True}

  def _tableCommand(self, cmd_dict):
    # TODO: Test
    # Processes a UI request for a Table
    # Input: cmd_dict - dictionary with the keys
    # Output: response - response to user
    target = "Table"
    error = None
    command = cmd_dict["command"]
    if command == "Export":
      args_list = cmd_dict['args']
      # TODO: Create correct format for argument in test
      if isinstance(args_list, list):
        if len(args_list) != 3:
          args_list = eval(cmd_dict['args'][0])
      POS_FUNC = 0
      POS_INPUTS = 1
      POS_OUTPUTS = 2
      function_name = args_list[POS_FUNC]
      inputs, error = self._extractListFromString(args_list[POS_INPUTS])
      if error is None:
        outputs, error = self._extractListFromString(args_list[POS_OUTPUTS])
        if error is None:
          file_name = "%s.py" % function_name
          file_path = os.path.join(st.SCISHEETS_USER_PYDIR, file_name)
          error = self.export(function_name=function_name,
                              inputs=inputs,
                              outputs=outputs,
                              file_path=file_path,
                              user_directory=st.SCISHEETS_USER_PYDIR,
                              import_path=st.SCISHEETS_USER_PYPATH)
          response = self._createResponse(error)
    elif command == "ListTableFiles":
      response = self._listTableFiles()
    elif command == "Open":
      file_name = cmd_dict['args'][0]
      file_path = os.path.join(st.BASE_DIR, "%s.pcl" % file_name)
      SET_CURRENT_FILE(file_path) # This is current in the session variable.
    elif command == "Rename":
      proposed_name = cmd_dict['args'][0]
      error = self.setName(proposed_name)
      response = self._createResponse(error)
    elif command == "Trim":
      self.trimRows()
      response = self._createResponse(error)
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    return response

  def _cellCommand(self, cmd_dict):
    # Processes a UI request for a Cell
    # Input: cmd_dict - dictionary with the keys
    # Output: response - response to user
    error = None
    command = cmd_dict["command"]
    if command == "Update":
      self.updateCell(cmd_dict["value"], 
                      cmd_dict["row_index"], 
                      cmd_dict["column_index"])
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    response = self._createResponse(error)
    return response

  def _columnCommand(self, cmd_dict):
    # Processes a UI request for a Column
    # Input: cmd_dict - dictionary with the keys
    # Output: response - response to user
    error = None
    command = cmd_dict["command"]
    column = self.columnFromIndex(cmd_dict["column_index"])
    if (command == "Append") or (command == "Insert"):
      name = cmd_dict["args"][0]
      error = Column.isPermittedName(name)
      if error is None:
        new_column = Column(name)
        increment = 0
        if command == "Append":
          increment = 1
        new_column_index = cmd_dict["column_index"] + increment
        self.addColumn(new_column, new_column_index)
    elif command == "Delete":
      self.deleteColumn(column)
    elif command == "Formula":
      formula = cmd_dict["args"][0]
      if len(formula.strip()) == 0:
        error = column.setFormula(None)
      else:
        error = column.setFormula(formula)
    elif command == "Move":
      dest_column_name = cmd_dict["args"][0]
      try:
        if dest_column_name == "LAST":
          new_column_index = self.numColumns() - 1
        else:
          dest_column = self.columnFromName(dest_column_name)
          new_column_index = self.indexFromColumn(dest_column)
        cur_column = self.columnFromIndex(cmd_dict["column_index"])
        self.moveColumn(cur_column, new_column_index)
      except Exception:
        error = "Column %s does not exist." % dest_column_name
    elif command == "Rename":
      proposed_name = cmd_dict["args"][0]
      if not self.renameColumn(column, proposed_name):
        error = "%s is a duplicate column name." % proposed_name
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    response = self._createResponse(error)
    return response

  def _rowCommand(self, cmd_dict):
    # Processes a UI request for a Row
    # Input: cmd_dict - dictionary with the keys
    # Output: response - response to user
    error = None
    command = cmd_dict["command"]
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
    response = self._createResponse(error)
    return response

  @staticmethod
  def _addEscapesToQuotes(iter_str):
    # Puts in the \ escape character for quotes, ' & "
    # Input: iterable of strings
    # Output: list with inserted escapes
    result = []
    for item in iter_str:
      if isinstance(item, str):
        new_item = item.replace('"', '\\\\"')
        newer_item = new_item.replace("'", "\\\\'")
        result.append(newer_item)
      else:
        result.append(item)
    return result
  
  def render(self, table_id="scitable"):
    # Input: table_id - how the table is identified in the HTML
    # Output: html rendering of the Table
    column_names = [c.getName() for c in self._columns]
    column_data = [c.getCells().tolist() for c in self._columns]
    raw_formulas = [c.getFormula() for c in self._columns]
    formulas = []
    for ff in raw_formulas:
      if ff is None or (ff == "None"):
        formulas.append("''")
      else:
        formulas.append('`' + ff + '`')
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
               }
    html = get_template('scitable.html').render(ctx_dict)
    return html

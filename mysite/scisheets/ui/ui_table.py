'''
  Extends the Table class to display a table and respond to UI events
'''

from ..core.table import Table
from ..core.column import Column
from ..core.errors import NotYetImplemented, InternalError
from mysite.helpers import util as ut
from mysite import settings as st
import collections
import numpy as np
import os
import random
import re


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
    table = cls(name)
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
      new_error = self.evaluate(user_directory=st.SCISHEETS_USER_PYDIR)
    else:
      new_error = error
    if new_error is None:
      response = {'data': "OK", 'success': True}
    else:
      response = {'data': str(new_error), 'success': False}
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
                              user_directory=st.SCISHEETS_USER_PYDIR)
          response = self._createResponse(error)
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
    raise InternalError("Must override render method.")

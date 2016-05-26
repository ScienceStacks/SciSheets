'''
  Extends the Table class to display a table and respond to UI events
'''

from scisheets.core.table import Table
from scisheets.core.column import Column
from scisheets.core.errors import NotYetImplemented, InternalError
from scisheets.core.helpers.cell_types import getType
from mysite import settings as st
import collections
import numpy as np
import os
import re


class UITable(Table):
  """
  Extends the Table class to provide rendering of the Table as
  a YUI DataTable.
  """

  def __init__(self, name):
    self._hidden_columns = []
    super(UITable, self).__init__(name)

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

  def unhideAllColumns(self):
    """
    Unmarks columns as as hidden.
    """
    self._hidden_columns = []

  def _cleanHiddenColumns(self):
    """
    Columns may be deleted at a lower level
    """
    self._hidden_columns = [c for c in self._hidden_columns  \
                            if c in self._columns]

  def hideColumns(self, columns):
    """
    Marks columns as as hidden.
    :param list-of-Column or Column: columns
    """
    self._cleanHiddenColumns()
    if isinstance(columns, Column):
      columns = [columns]
    for column in columns:
      if not column in self._hidden_columns:
        self._hidden_columns.append(column)

  def unhideColumns(self, columns):
    """
    Unmarks columns as as hidden.
    :param list-of-Column or Column: columns
    """
    self._cleanHiddenColumns()
    if isinstance(columns, Column):
      columns = [columns]
    for column in columns:
      if column in self._hidden_columns:
        self._hidden_columns.remove(column)

  def getVisibleColumns(self):
    """
    :return list-of-Columns:
    """
    vis_columns = [c for c in self._columns  \
                   if not c in self._hidden_columns]
    return vis_columns

  def visibleColumnFromIndex(self, index):
    """
    Eliminates hidden columns when computing index.
    :param int index:
    :return Column:
    """
    return self.getVisibleColumns()[index]

  def getHiddenColumns(self):
    self._cleanHiddenColumns()
    return self._hidden_columns

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
    versioned = self.getVersionedFile()
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
          error = self.export(function_name=function_name,
                              inputs=inputs,
                              outputs=outputs,
                              user_directory=st.SCISHEETS_USER_PYDIR)
      response = self._createResponse(error)
    elif command == "Open":
      file_name = cmd_dict['args'][0]
      file_path = os.path.join(st.BASE_DIR, "%s.pcl" % file_name)
      SET_CURRENT_FILE(file_path) # This is current in the session variable.
    elif command == "Redo":
      try:
        versioned.redo()
        error = None
      except Exception as err:
        error = str(err)
      response = self._createResponse(error)
    elif command == "Rename":
      versioned.checkpoint()
      proposed_name = cmd_dict['args'][0]
      error = self.setName(proposed_name)
      response = self._createResponse(error)
    elif command == "Trim":
      versioned.checkpoint()
      self.trimRows()
      response = self._createResponse(error)
    elif command == "Undo":
      try:
        versioned.undo()
        error = None
      except Exception as err:
        error = str(err)
      response = self._createResponse(error)
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    return response

  def _cellCommand(self, cmd_dict):
    # Processes a UI request for a Cell
    # Input: cmd_dict - dictionary with the keys
    # Output: response - response to user
    types = [int, str, bool, unicode]
    error = None
    command = cmd_dict["command"]
    versioned = self.getVersionedFile()
    if command == "Update":
      versioned.checkpoint()
      column = self.visibleColumnFromIndex(cmd_dict["column_index"])
      if column.getTypeForCells() == object:
        error = "Cannot update cells for the types in column %s"  \
           % column.getName()
      else:
        value = cmd_dict["value"]
        value_type = getType(value)
        if value_type  == object:
          value = str(value)
        self.updateCell(value,
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
    column = self.visibleColumnFromIndex(cmd_dict["column_index"])
    versioned = self.getVersionedFile()
    if (command == "Append") or (command == "Insert"):
      versioned.checkpoint()
      name = cmd_dict["args"][0]
      error = Column.isPermittedName(name)
      if error is None:
        new_column = Column(name)
        increment = 0
        if command == "Append":
          increment = 1
        column_index = self.indexFromColumn(column)
        new_column_index = column_index + increment
        self.addColumn(new_column, new_column_index)
    elif command == "Delete":
      versioned.checkpoint()
      self.deleteColumn(column)
    elif command == "Formula":
      versioned.checkpoint()
      formula = cmd_dict["args"][0]
      if len(formula.strip()) == 0:
        error = column.setFormula(None)
      else:
        error = column.setFormula(formula)
    elif command == "Move":
      versioned.checkpoint()
      dest_column_name = cmd_dict["args"][0]
      try:
        if dest_column_name == "LAST":
          new_column_index = self.numColumns() - 1
        else:
          dest_column = self.columnFromName(dest_column_name)
          new_column_index = self.indexFromColumn(dest_column)
        cur_column = self.visibleColumnFromIndex(cmd_dict["column_index"])
        self.moveColumn(cur_column, new_column_index)
      except Exception:
        error = "Column %s does not exist." % dest_column_name
    elif command == "Refactor":
      versioned.checkpoint()
      proposed_name = cmd_dict["args"][0]
      try:
        self.refactorColumn(column.getName(), proposed_name)
      except Exception as err:
        error = str(err)
    elif command == "Rename":
      versioned.checkpoint()
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
    versioned = self.getVersionedFile()
    if command == "Move":
      versioned.checkpoint()
      new_name = cmd_dict["args"][0]
      self.renameRow(row_index, new_name)
    elif command == "Delete":
      versioned.checkpoint()
      self.deleteRows([row_index])
    elif command == "Insert":
      versioned.checkpoint()
      row = self.getRow()
      self.addRow(row, row_index - 0.1)  # Add a new row before 
    elif command == "Append":
      versioned.checkpoint()
      row = self.getRow()
      self.addRow(row, row_index + 0.1)  # Add a new row after
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    response = self._createResponse(error)
    return response

  def migrate(self):
    """
    Handles older objects that lack some properties
    """
    if not '_hidden_columns' in dir(self):
      self._hidden_columns = []
    super(UITable, self).migrate()

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

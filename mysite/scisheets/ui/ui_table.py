'''
  Extends the Table class to display a table and respond to UI events
'''

from scisheets.core.table import Table
from scisheets.core.column import Column
from scisheets.core.errors import NotYetImplemented, InternalError
from scisheets.core.helpers.cell_types import getType
from mysite import settings as settings
import collections
import numpy as np
import os
import re


class _Response(dict):
  """
  Object provided in response to a UI request
  """

  def __init__(self, error):
    """
    :param Exception error:
    """
    if error is None:
      self['data'] = "OK"
      self['success'] = True
    else:
      self['data'] = str(error)
      self['success'] = False


class UITable(Table):
  """
  Extends the Table class to provide rendering of the Table as
  a YUI DataTable.
  """

  def __init__(self, name):
    super(UITable, self).__init__(name)
    self._hidden_children = []

  def getSerializationDict(self, class_variable):
    """
    :param str class_variable: key to use for the class name
    :return dict: dictionary encoding the object
    """
    serialization_dict =   \
        super(UITable, self).getSerializationDict(class_variable)
    serialization_dict[class_variable] = str(self.__class__)
    child_names = [c.getName() for c in self._hidden_children]
    serialization_dict['_hidden_children'] = child_names
    return serialization_dict

  @classmethod
  def deserialize(cls, serialization_dict, instance=None):
    """
    Deserializes an UITable object and does fix ups.
    :param dict serialization_dict: container of parameters for deserialization
    :return UITable (or instance updated)
    """
    if instance is None:
      instance = UITable(serialization_dict["_name"])
    super(UITable, cls).deserialize(serialization_dict,
        instance=instance)
    if "_hidden_children" in serialization_dict:
      key = "_hidden_children"
    else:
      key = "_hidden_columns"
    hidden_children = [instance.childFromName(n, is_relative=False) 
                       for n in serialization_dict[key]]
    instance.hideChildren(hidden_children)
    return instance

  @staticmethod
  def _versionCheckpoint(versioned, target, command):
    if versioned is not None:
      versioned.checkpoint(id="%s/%s" % (target, command))

  def _createResponse(self, error):
    # Returns a response of the desired type
    # Input: error - result of processing a command
    #                (may be None)
    # _Response
    if error is None:
      new_error = self.evaluate(user_directory=settings.SCISHEETS_USER_PYDIR)
    else:
      new_error = error
    return _Response(new_error)

  def isEquivalent(self, other, is_exception=False):
    """
    :param UITable other:
    :param bool is_exception: generate an AssertionError if false
    :return bool: True if equivalent
    """
    msg = None
    if not super(UITable, self).isEquivalent(other, 
        is_exception=is_exception):
      msg = "Failed equivalence in ancestor of UITable."
    elif not len(self.getHiddenNodes()) == len(other.getHiddenNodes()):
      msg = "Hidden Nodes are not equivalent"
    else:
      for column in self.getHiddenNodes():
        tests = [column.isEquivalent(c) for c in other.getHiddenNodes()]
        if not any(tests):
          msg = "Column %s is not hidden" % column.getName()
          break
    if msg is None:
      return True
    else:
      if is_exception:
        raise AssertionError(msg)
      else:
        return False

  def copy(self, instance=None):
    """
    Returns a copy of this object
    :param UITable instance:
    """
    # Create an object if one is not provided
    if instance is None:
      instance = UITable(self.getName(is_global_name=False))
    # Copy properties from inherited classes
    instance = super(UITable, self).copy(instance=instance)
    # Set properties specific to this class
    instance._hidden_children = self._hidden_children
    return instance

  def unhideAllChildren(self):
    """
    Unmarks children as as hidden.
    """
    self._hidden_children = []

  def _cleanHiddenChildren(self):
    """
    Children may be deleted at a lower level
    """
    self._hidden_children = [c for c in self._hidden_children  \
                            if c in self.getAllNodes()]

  def hideChildren(self, children):
    """
    Marks children as as hidden.
    :param list-of-NamedTree or NamedTree: children
    """
    if not isinstance(children, list):
      children = [children]
    for child in children:
      if not child in self._hidden_children:
        self._hidden_children.append(child)

  def unhideChildren(self, children):
    """
    Unmarks children as as hidden.
    :param list-of-Column or Column: children
    """
    if isinstance(children, Column):
      children = [children]
    for child in children:
      if child in self._hidden_children:
        self._hidden_children.remove(child)

  def isHiddenChild(self, child):
    return child in self._hidden_children

  def getVisibleNodes(self):
    """
    Considers the node hierarchy when determining which nodes are visible.
    A child is not visible if it's parent is hidden.
    :return list-of-NamedTree:
    """
    visibles = []
    nodes = self.getAllNodes()
    nodes.remove(self)
    for node in nodes:
      path = node.findNodesFromRoot()
      is_visible = True
      for ancestor in path:
        if ancestor in self._hidden_children:
          is_visible = False
          break
      if is_visible:
        visibles.append(node)
    return visibles

  def getVisibleColumns(self):
    """
    :return list-of-Column:
    """
    return [c for c in self.getVisibleNodes() if isinstance(c, Column)]

  def getHiddenNodes(self):
    """
    :return list-of-ColumnContainer:
    """
    visibles = set(self.getVisibleNodes())
    nodes = self.getAllNodes()
    nodes.remove(self)
    hiddens = set(nodes).difference(visibles)
    return list(hiddens)

  def processCommand(self, cmd_dict):
    # Processes a UI request for the Table.
    # Input: cmd_dict - dictionary with the keys
    #          target - type of table object targeted: Cell, Column, Row
    #          command - command issued
    #          table_name - name of the table
    #          column_name - full path name
    #          row_index - 0 based index of row
    #          value - value assigned
    # Output: response, is_save - Dictionary with response
    #            data: data returned
    #            success: True/False
    #         is_save - bool (if should save table)
    target = cmd_dict["target"]
    is_save = True
    if target == "Cell":
      response = self._cellCommand(cmd_dict)
    elif target == "Column":
      response = self._columnCommand(cmd_dict)
    elif target == "Row":
      response = self._rowCommand(cmd_dict)
    elif target == "Table":
      response, is_save = self._tableCommand(cmd_dict)
    elif target == "Sheet":
      response, is_save = self._sheetCommand(cmd_dict)
    else:
        msg = "Unimplemented %s." % target
        raise NotYetImplemented(msg)
    return response, is_save

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

  def _commandTablize(self, cmd_dict):
    """
    Inserts a Table above the current column or table.
    :param CommandDict cmd_dict:
    :return str error:
    """
    proposed_name = cmd_dict['args'][0]
    table = UITable("temporary")
    error = table.setName(proposed_name)
    if error is None:
      child = self.childFromName(cmd_dict["column_name"], is_all=True)
      parent = child.getParent()
      position = child.getPosition()
      child.removeTree()
      parent.addChild(table, position)
      table.addChild(child)
    return error

  def _tableCommand(self, cmd_dict):
    # TODO: Test
    # Processes a UI request for a Table
    # Input: cmd_dict - dictionary with the keys
    # Output: response, is_save - response to user
    #         is_save - bool (if should save table)
    target = "Table"
    table = self.childFromName(cmd_dict["column_name"], is_all=True)
    is_save = True
    error = None
    command = cmd_dict["command"]
    argument = cmd_dict.getFirstArgument()
    versioned = self.getVersionedFile()
    if (command == "Append") or (command == "Insert"):
      error = self._commandAppendAndInsert(table, target, command, argument)
    elif command == "Delete":
      table.removeTree()
    elif command == "Epilogue":
      epilogue = cmd_dict['args'][0]
      error = table.setEpilogue(epilogue)
    elif command == "Hide":
      UITable._versionCheckpoint(versioned, target, command)
      self.hideChildren([table])
    elif command == "Move":
      UITable._versionCheckpoint(versioned, target, command)
      dest_child_name = argument
      dest_child = self.childFromName(dest_child_name, is_relative=False)
      table = self.childFromName(cmd_dict["column_name"])
      try:
       self.moveChildToOtherchild(table, dest_child)
      except Exception:
        import pdb; pdb.set_trace()
        error = "%s does not exists." % dest_child_name
    elif command == "Prologue":
      prologue = cmd_dict['args'][0]
      error = table.setPrologue(prologue)
    elif command == "Rename":
      UITable._versionCheckpoint(versioned, target, command)
      proposed_name = cmd_dict['args'][0]
      error = table.setName(proposed_name)
    elif command == "Tablize":
      UITable._versionCheckpoint(versioned, target, command)
      error = self._commandTablize(cmd_dict)
    elif command == "Trim":
      UITable._versionCheckpoint(versioned, target, command)
      table.trimRows()
    elif command == "Unhide":
      UITable._versionCheckpoint(versioned, target, command)
      self.unhideChildren([table])
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    response = self._createResponse(error)
    return response, is_save

  def _sheetCommand(self, cmd_dict):
    # TODO: Test
    # Processes a UI request for a Table
    # Input: cmd_dict - dictionary with the keys
    # Output: response, is_save - response to user
    #         is_save - bool (if should save table)
    target = "Sheet"
    is_save = True
    error = None
    command = cmd_dict["command"]
    versioned = self.getVersionedFile()
    if command == "Export":
      args_list = cmd_dict['args']
      # TODO: Create correct format for argument in test
      if isinstance(args_list, list):
        if len(args_list) != 3:
          args_list = eval(cmd_dict['args'][0])
      pos_func = 0  # Position of the function name
      pos_inputs = 1  # Position of the list of input column names
      pos_outputs = 2  # Position of the list of output column names
      function_name = args_list[pos_func]
      inputs, error = self._extractListFromString(args_list[pos_inputs])
      if error is None:
        outputs, error = self._extractListFromString(args_list[pos_outputs])
        if error is None:
          error = self.export(function_name=function_name,
                              inputs=inputs,
                              outputs=outputs,
                              user_directory=settings.SCISHEETS_USER_PYDIR)
      if error is not None:
        is_save = False
      response = self._createResponse(error)
    elif command == "Redo":
      try:
        versioned.redo()
        error = None
      except Exception as err:
        error = str(err)
      response = self._createResponse(error)
      is_save = False
    elif command == "Undo":
      try:
        versioned.undo()
        error = None
      except Exception as err:
        error = str(err)
      response = self._createResponse(error)
      is_save = False
    elif command == "Unhide":
      UITable._versionCheckpoint(versioned, target, command)
      self.unhideAllChildren()
      response = self._createResponse(error)
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    return response, is_save

  def _cellCommand(self, cmd_dict):
    # Processes a UI request for a Cell
    # Input: cmd_dict - dictionary with the keys
    # Output: response - response to user
    types = [int, str, bool, unicode]
    target = "Cell"
    error = None
    command = cmd_dict["command"]
    versioned = self.getVersionedFile()
    if command == "Update":
      UITable._versionCheckpoint(versioned, target, command)
      name = cmd_dict["column_name"]
      column = self.childFromName(name)
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
                        cmd_dict["column_name"])
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    response = self._createResponse(error)
    return response

  def _isDuplicateInGlobalScope(self, name):
    """
    Checks if the local name duplicates other local names in the global scope of column names.
    :param str name:
    :return bool: True if duplicate
    """
    global_names = [c.getName() for c in self.getChildren(is_recursive=True)]
    return name in global_names

  def _commandAppendAndInsert(self, node, target, command, name):
    """
    Processes Append and Insert commands for targets of Column and Table.
    :param NamedTree node:
    :param str target:
    :param str command:
    :param str name: name for new Column
    :return str error:
    """
    versioned = self.getVersionedFile()
    UITable._versionCheckpoint(versioned, target, command)
    error = Column.isPermittedName(name)
    if self._isDuplicateInGlobalScope(name):
      error = "%s conflics with existing names" % proposed_name
    if error is None:
      new_column = Column(name)
      increment = 0
      if command == "Append":
        increment = 1
      parent = node.getParent()
      column_index = node.getPosition()
      new_column_index = column_index + increment
      parent.addChild(new_column, new_column_index)
    return error

  def _columnCommand(self, cmd_dict):
    # Processes a UI request for a Column
    # Input: cmd_dict - dictionary with the keys
    # Output: response - response to user
    error = None
    target = "Column"
    command = cmd_dict["command"]
    column = self.childFromName(cmd_dict["column_name"],
        is_relative=False)
    versioned = self.getVersionedFile()
    argument = cmd_dict.getFirstArgument()
    if (command == "Append") or (command == "Insert"):
      error = self._commandAppendAndInsert(column, target, command, argument)
    elif command == "Delete":
      UITable._versionCheckpoint(versioned, target, command)
      column.removeTree()
      self._cleanHiddenChildren()
    elif command == "Formula":
      UITable._versionCheckpoint(versioned, target, command)
      formula = argument
      if len(formula.strip()) == 0:
        error = column.setFormula(None)
      else:
        error = column.setFormula(formula)
    elif command == "Hide":
      if not column in self.getHiddenNodes():
        self.hideChildren([column])
    elif command == "Move":
      UITable._versionCheckpoint(versioned, target, command)
      dest_column_name = argument
      dest_column = self.childFromName(dest_column_name, is_relative=False)
      cur_column = self.childFromName(cmd_dict["column_name"])
      try:
       self.moveChildToOtherchild(cur_column, dest_column)
      except Exception:
        error = "Column %s does not exists." % dest_column_name
    elif command == "Refactor":
      UITable._versionCheckpoint(versioned, target, command)
      proposed_name = argument
      if self._isDuplicateInGlobalScope(proposed_name):
        error = "%s conflics with existing names" % proposed_name
      else:
        try:
          self.refactorColumn(column.getName(), proposed_name)
        except Exception as err:
          error = str(err)
    elif command == "Rename":
      UITable._versionCheckpoint(versioned, target, command)
      proposed_name = argument
      is_error = False
      if self._isDuplicateInGlobalScope(proposed_name):
        is_error = True
      if (not is_error) and   \
          not self.renameColumn(column, proposed_name):
        is_error = True
      if is_error:
        error = "%s is a duplicate column name." % proposed_name
    elif command == "Tablize":
      UITable._versionCheckpoint(versioned, target, command)
      error = self._commandTablize(cmd_dict)
    elif command == "Unhide":
      self.unhideChildren([column])
    else:
      msg = "Unimplemented %s command: %s." % (target, command)
      raise NotYetImplemented(msg)
    response = self._createResponse(error)
    return response

  def _rowCommand(self, cmd_dict):
    """
    Processes a UI request for a Row
    :param dict cmd_dict: - dictionary with the keys
    :return dict: keys are data and success
    Handles detached tables by determining the lowest
    table in the table tree that issued the command.
    """
    error = None
    target = "Row"
    command = cmd_dict["command"]
    column_name = cmd_dict["column_name"]
    column = self.columnFromName(column_name)
    table = column.getParent()
    row_index = cmd_dict['row_index']
    versioned = self.getVersionedFile()
    if command == "Move":
      if versioned is not None:
        versioned.checkpoint(id="%s/%s" % (target, command))
      new_name = cmd_dict["args"][0]
      table.renameRow(row_index, new_name)
    elif command == "Delete":
      if versioned is not None:
        versioned.checkpoint(id="%s/%s" % (target, command))
      table.deleteRows([row_index])
    elif command == "Insert":
      UITable._versionCheckpoint(versioned, target, command)
      row = self.getRow()
      table.addRow(row, row_index - 0.1)  # Add a new row before 
    elif command == "Append":
      UITable._versionCheckpoint(versioned, target, command)
      row = self.getRow()
      table.addRow(row, row_index + 0.1)  # Add a new row after
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

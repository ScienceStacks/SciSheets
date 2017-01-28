'''
  Implements the table class for SciSheets.
'''
from mysite import settings
import mysite.helpers.util as ut
from mysite.helpers.data_capture import DataCapture
from mysite.helpers.versioned_file import VersionedFile
from helpers.formula_statement import FormulaStatement
from helpers.is_null import isNull
from column import Column
from column_container import ColumnContainer
from table_evaluator import TableEvaluator
from helpers.serialize_deserialize import deserialize
import errors as er
import json
import numpy as np
import os
import pandas as pd
import random

NAME_COLUMN_STR = "row"
NAME_COLUMN_IDX = 0
CUR_DIR = os.path.dirname(__file__)
PROLOGUE_FILEPATH = os.path.join(CUR_DIR, "table.prologue")
EPILOGUE_FILEPATH = os.path.join(CUR_DIR,"table.epilogue")
PROLOGUE_NAME = "Prologue"
EPILOGUE_NAME = "Epilogue"


class Row(dict):
  """
  Container of values for a row
  """
  pass


# pylint: disable=R0904
class Table(ColumnContainer):
  """
  Implements full table functionality.
  Feature 1: Maintains consistency
    between columns as to column lengths
    column names are unique
  Feature 2: Knows about rows
    add rows
    delete rows
    rows have a name as specified in the row column
  The primary object for referencing a column is the column object.
  The primary object for referencing a row is the row index
  """

  def __init__(self, name):
    super(Table, self).__init__(name)
    self._namespace = {}  # Namespace for formula evaluation
    self._createNameColumn()
    self._prologue = self._formulaStatementFromFile(PROLOGUE_FILEPATH,
        PROLOGUE_NAME)
    self._epilogue = self._formulaStatementFromFile(EPILOGUE_FILEPATH,
        EPILOGUE_NAME)
    self._is_evaluate_formulas = True

  @classmethod
  def createRandomTable(cls, name, nrow, ncol, ncolstr=0,
        low_int=0, hi_int=100, table_cls=None):
    """
    Creates a table with random integers as values
    Input: name - name of the table
           nrow - number of rows
           ncol - number of columns
           ncolstr - number of columns with strings
           low_int - smallest integer
           hi_int - largest integer
           table_cls - Table class to use; default is Table
    """
    if table_cls is None:
      table_cls = cls
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

  @classmethod
  def createRandomHierarchicalTable(cls, name, nrow, num_nodes, 
      prob_child, ncolstr=0, low_int=0, hi_int=100, prob_detach=0,
      table_cls=None):
    """
    Creates a table with random integers as values
    :param str name: name of the table
    :param int nrow: number of rows
    :param float prob_child: probability that next node is a child
    :param str ncolstr: number of columns with strings
    :param int low_int: smallest integer
    :param int hi_int: largest integer
    :param float prob_detach: probability that a subtree is detached
    :parm Type table_cls: Table class to use; default is Table
    :return table_cls:
    """
    if table_cls is None:
      table_cls = cls
    # Create the schema for the Hierarchical Table
    htable = super(Table, cls).createRandomNamedTree(num_nodes, 
        prob_child, leaf_cls=Column, prob_detach=prob_detach, 
        nonleaf_cls=table_cls)
    leaves = [c for c in htable.getLeaves() 
              if c.getName(is_global_name=False) != NAME_COLUMN_STR]
    num_leaves = len(htable.getLeaves()) -1  # Don't include the name column
    # Create the values for the leaves of the Hierarchical Table
    flat_table = Table.createRandomTable(name, nrow, num_leaves, ncolstr=ncolstr,
        low_int=low_int, hi_int=hi_int, table_cls=table_cls)
    data_columns = flat_table.getDataColumns()
    pairs = zip(leaves, data_columns)
    # Populate the leaves of the Hierarchical Table
    [htable.addCells(l, d.getCells(), replace=True) for l, d in pairs]
    return htable

  def getSerializationDict(self, class_variable):
    """
    :param str class_variable: key to use for the class name
    :return dict: dictionary encoding the Table object and its columns
    """
    serialization_dict = {}
    serialization_dict[class_variable] = str(self.__class__)
    filepath = self.getFilepath()
    if self.getFilepath() is not None:
      if ut.getFileExtension(self.getFilepath()) != settings.SCISHEETS_EXT:
        filepath = ut.changeFileExtension(self.getFilepath(), 
            settings.SCISHEETS_EXT)
    more_dict = {
        "_name": self.getName(is_global_name=False),
        "_prologue_formula": self.getPrologue().getFormula(),
        "_epilogue_formula": self.getEpilogue().getFormula(),
        "_is_evaluate_formulas": self.getIsEvaluateFormulas(),
        "_filepath": filepath,
        "_attached": self.isAttached(),
        }
    serialization_dict.update(more_dict)
    _children = []
    for child in self.getChildren():
      if not Table.isNameColumn(child):
        _children.append(child.getSerializationDict(class_variable))
    serialization_dict["_children"] = _children
    return serialization_dict

  @classmethod
  def deserialize(cls, serialization_dict, instance=None):
    """
    Deserializes a table object and does fix ups.
    :param dict serialization_dict: container of parameters for deserialization
    :return Table:
    """
    if instance is None:
      table = Table(serialization_dict["_name"])
    else:
      table = instance
    if serialization_dict["_filepath"] is not None:
      table.setFilepath(serialization_dict["_filepath"])
    table.setPrologue(serialization_dict["_prologue_formula"])
    table.setEpilogue(serialization_dict["_epilogue_formula"])
    table.setIsEvaluateFormulas(serialization_dict["_is_evaluate_formulas"])
    if "_attached" in serialization_dict.keys():
      table.setIsAttached(serialization_dict["_attached"])
    if "_children" in serialization_dict.keys():
      child_dicts = serialization_dict["_children"]
    elif "_columns" in serialization_dict.keys():
      child_dicts = serialization_dict["_columns"]
    else:
      raise ValueError("Cannot find children for %s" % table.getName())
    for child_dict in child_dicts:
      # Handle older serializations
      if not child_dict['_name'] == NAME_COLUMN_STR:
        new_child = deserialize(json.dumps(child_dict))
        table.addChild(new_child)
    table.adjustColumnLength()
    return table


  # The following methods are used in debugging

  def d(self):
    return [(c.getName(), c.getCells()) for c 
            in self.getLeaves()]

  def f(self):
    return [(c.getName(), c.getFormula()) 
            for c in self.getColumns(is_attached=False)]

  def setCapture(self, filename, data):
    dc = DataCapture(filename)
    dc.setData(data)
 
  def getIsEvaluateFormulas(self):
    return self._is_evaluate_formulas
  
  # Internal and other methods

  # TODO: Tests with multiple levels of subtable
  def _updateNameColumn(self, nrows_table=None):
    """
    Changes the cells in the name column of the table
    to be consecutive ints.
    :paam int nrows_table: Number of rows in the table
    """
    if nrows_table is None:
      nrows_table = self.numRows()
    names = []
    for row_num in range(nrows_table):
      names.append(Table._rowNameFromIndex(row_num))
    for column in self.getLeaves(is_attached=True):
      if Table.isNameColumn(column):
        column.addCells(list(names), replace=True)

  def _formulaStatementFromFile(self, filepath, name):
    """
    Reads the file contents and creates the FormulaStatement object.
    :param str filepath: path to file to read
    :param str name: name of the formula
    :returns str: file contents
    """
    with open(filepath, 'r') as f:
      lines = f.readlines()
    statements = ''.join(lines)
    return FormulaStatement(statements, name)

  # Data columns are those that have user data. The "row" column is excluded.
  def getDataColumns(self):
    """
    Returns the columns other than the name column
    """
    return [c for c in self.getColumns() if not Table.isNameColumn(c)]

  def getNameColumn(self):
    """
    Gets the name column for this table.
    :return Column:
    """
    columns = [c for c in self.getColumns() 
               if Table.isNameColumn(c) and c.getParent() == self]
    if len(columns) != 1:
      raise RuntimeError("Should have exactly one name column")
    return columns[0]

  def getData(self):
    """
    :return dict: keys are global column names
    """
    return {c.getName(): list(c.getCells())
            for c in self.getColumns(is_recursive=True)
            if not Table.isNameColumn(c)}

  def getEpilogue(self):
    """
    :return FormulaStatement:
    """
    return self._epilogue

  def getFormulaColumns(self):
    """
    :return list-of-Column:
    """
    result = [c for c in self.getColumns(is_attached=False) 
              if c.getFormula() is not None]
    return result

  def getRow(self, row_index=None):
    """
    :param row_index: row desired
           if None, then a row of None is returned
    :return: Row object
    """
    row = Row()
    for column in self.getColumns(is_recursive=True):
      if row_index is None:
        if column.isFloats():
          row[column.getName()] = np.nan  # pylint: disable=E1101
        else:
          row[column.getName()] = None
      else:
        row[column.getName()] = column.getCells()[row_index]
    return row

  def getNamespace(self):
    return self._namespace

  def getPrologue(self):
    """
    :return FormulaStatement:
    """
    return self._prologue

  # TODO: Verify the index
  @staticmethod
  def _rowNameFromIndex(index):
    """
    Create the row name from its index
    """
    return str(index + 1)

  def _coerceNameColumnToStr(self):
    """
    Makes sure that row names are strings
    """
    column = self.columnFromName(NAME_COLUMN_STR)
    if column is None:
      import pdb; pdb.set_trace()
    values = [str(v) for v in column.getCells()]
    column.replaceCells(values)

  # TODO: Verify the index
  @staticmethod
  def _rowNamesFromSize(size):
    """
    :param size: number of rows
    :return: array of names
    """
    return [str(n) for n in range(1, size+1)]

  def _createNameColumn(self):
    """
    Creates the name column for the table
    """
    column = Column(NAME_COLUMN_STR, asis=True)
    self.addColumn(column)

  def adjustColumnLength(self):
    """
    Inserts values of None or np.nan so that column
        has the same length as the table
    """
    none_array = np.array([None])
    num_rows = self.numRows()
    for column in self.getColumns():
      adj_rows = num_rows - column.numCells()
      if adj_rows > 0:
        if column.isFloats():
          column.addCells(np.repeat(np.nan, adj_rows))  # pylint:disable=E1101
        else:
          column.addCells(np.repeat(none_array, adj_rows))
    self._updateNameColumn(nrows_table=num_rows)

  def _validateTable(self):
    """
    Checks that the table is internally consistent
    Verify that there is at least one column
    """
    if len(self.getColumns()) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    # Verify that all columns have the same number of cells
    name_column = self.columnFromName(NAME_COLUMN_STR)
    if name_column is None:
      import pdb; pdb.set_trace()
    num_rows = self.numRows()
    for column in self.getColumns():
      if  column.numCells() != num_rows:
        import pdb; pdb.set_trace()
        msg = "In Table %s, Column %s differs in its number of rows." \
            % (self.getName(), column.getName())
        raise er.InternalError(msg)
    # Verify that the first Column is the Name Column
    if self.getChildAtPosition(0).getName(is_global_name=False) != NAME_COLUMN_STR:
      msg = "In Table %s, first column is not 'row' column" % self.getName()
      raise er.InternalError(msg)
    # Verify that names are unique
    if self.validateTree() is not None:
      raise RuntimeError(self.validateTree())
    # Verify the sequence of row names
    for nrow in range(self.numRows()):
      expected_row_name = Table._rowNameFromIndex(nrow)
      actual_row_name =  \
          self.getChildAtPosition(NAME_COLUMN_IDX).getCells()[nrow]
      if actual_row_name != expected_row_name:
        import pdb; pdb.set_trace()
        msg = "In Table %s, invalid row name at index %d: %s" % \
                (self.getName(), nrow, actual_row_name)
        raise er.InternalError(msg)
    # Verify that the name columns are identical
    for column in self.getColumns():
      if Table.isNameColumn(column):
        if not column.getCells() == name_column.getCells():
          raise RuntimeError("%s is not a consistent name column" % column.getName())

  def addCells(self, column, cells, replace=False):
    """
    Adds to the column
    :param Column column:
    :param list cells:
    """
    column.addCells(cells, replace=replace)
    self.adjustColumnLength()
    self._validateTable()

  def addColumn(self, column, index=None):
    """
    Adds a column to the table.
    Adjusts the Column length to that of the table
    :param column: column object
    :param int index: position for the new column
    :return: error text if there is a problem with the column
                    None if no problem
    Notes: (1) A new column may have either no cells
               or the same number as the existing table
    """
    error = None
    # Check for problems with this column
    is_ok = all([c.getName(is_global_name=False) 
        != column.getName(is_global_name=False) 
        for c in self.getChildren()])
    if not is_ok:
      error = "**%s is a duplicate name" % column.getName()
      return error
    else:
      error = Column.isPermittedName(  \
          column.getName(is_global_name=False))
      if error is not None:
        return error
    if index is None:
      index = len(self.getColumns(is_attached=False))
    # Handle the different cases of adding a column
    self.addChild(column, position=index)
    # Case 1: First column after name column
    if self.numColumns() == 1:
      self._updateNameColumn()
    # Case 2: Subsequent columns
    else:
      self.adjustColumnLength()
    self._validateTable()

  def addRow(self, row, row_index=None):
    """
    :param Row row: Row to add
    :param int row_index: index where Row is added, may be a float
                       if None, then appended
    """
    # Determine the actual desired name
    if row_index is None:
      proposed_name = Table._rowNameFromIndex(self.numRows())
    else:
      proposed_name = Table._rowNameFromIndex(row_index)
    # Assign values to the last row of each column cells
    for column in self.getColumns(is_recursive=True):
      if column.getName(is_global_name=False) != NAME_COLUMN_STR:
        cur_name = column.getName()
        if cur_name in row:
          column.insertCell(row[cur_name])
        else:
          column.insertCell(None)
      else:
        column.insertCell(None)
    last_index = self.numRows() - 1
    self.renameRow(last_index, proposed_name)  # put the row in the right place
    self._validateTable()

  def copy(self, instance=None):
    """
    Returns a copy of this object
    :param Table instance:
    """
    # Create an object if none provided
    if instance is None:
      instance = Table(self.getName(is_global_name=False))
    name_column = instance.columnFromName(NAME_COLUMN_STR)
    instance.deleteColumn(name_column)  # Avoid duplicate
    # Copy everything required from inherited classes
    super(Table, self).copy(instance=instance)
    instance._coerceNameColumnToStr()
    # Set properties specific to this class
    instance.setPrologue(self.getPrologue().getFormula())
    instance.setEpilogue(self.getEpilogue().getFormula())
    instance.setIsEvaluateFormulas(self.getIsEvaluateFormulas())
    self.adjustColumnLength()
    return instance

  def deleteColumn(self, node):
    """
    Deletes a node from the table.
    :param column: column obj to delete
    """
    if isinstance(node, Column):
      self.removeColumn(node)
    else:
      node.removeTree()

  def deleteRows(self, indicies):
    """
    Deletes rows
    :param indicies: index of rows to delete
    """
    indicies.sort()
    indicies.reverse()
    for column in self.getColumns():
      column.deleteCells(indicies)
    self._updateNameColumn()

  def export(self, **kwargs):
    """
    Exports the table to a python program
    :return: error - string from the file export
    """
    table_evaluator = TableEvaluator(self)
    error = table_evaluator.export(**kwargs)
    return error

  def evaluate(self, user_directory=None):
    """
    Evaluates formulas in the table
    :param user_directory: full directory path where user modules
                            are placed
    :return: error from table evaluation or None
    """
    evaluator = TableEvaluator(self)
    error = evaluator.evaluate(user_directory=user_directory)
    return error

  def isColumnPresent(self, column_name):
    """
    :param str column_name:
    :return bool: True if column is present
    """
    return any([c.getName() == column_name 
                for c in self.getColumns(is_attached=False)])

  def isEquivalent(self, other_table):
    """
    Checks that the tables have the same values of their properties,
    excluding the VersionedFile.
    :param Table other_table:
    :returns bool:
    """
    local_debug = False # Breaks on specifc reasons for non-equiv
    if not isinstance(other_table, self.__class__):
      if local_debug:
        import pdb; pdb.set_trace()
      return False
    is_same_properties = (self.getName(is_global_name=False) == other_table.getName(is_global_name=False)) and  \
        (self.numColumns() == other_table.numColumns()) and  \
        (self.getPrologue().isEquivalent(other_table.getPrologue())) and  \
        (self.getEpilogue().isEquivalent(other_table.getEpilogue()))
    if not is_same_properties:
      if local_debug:
        import pdb; pdb.set_trace()
      return False
    if not super(Table, self).isEquivalent(other_table):
      if local_debug:
        import pdb; pdb.set_trace()
      return False
    return True

  @staticmethod
  def isNameColumn(column):
    """
    Determines if this is a name column
    :param Column column:
    :return bool: True if name column
    """
    path = column.pathFromGlobalName(column.getName())
    return path[-1] == NAME_COLUMN_STR

  @classmethod
  def isTable(cls, child):
    """
    :param NamedTree child:
    :return bool: True if is a Column
    """
    return isinstance(child, Table)
    
  def insertRow(self, row, index=None):
    """
    Inserts the row in the desired index in the table and
    assigns the value of the NAME_COLUMN
    :param row: a Row
    :param index: index in the table where the row is inserted
    """
    idx = index
    if idx is None:
      idx = self.numRows()
    for child in self.getLeaves(is_attached=True):
      if ColumnContainer.isColumn(child):
        name = child.getName(is_global_name=False)
        if name in row.keys():
          child.insertCell(row[name], idx)
        else:
          child.insertCell(None, idx)
    self._updateNameColumn()

  def moveRow(self, index1, index2):
    """
    Moves the row at index1 to index2
    """
    row = self.getRow(row_index=index1)
    self.deleteRows([index1])
    self.insertRow(row, index2)
    self._updateNameColumn()

  def numRows(self):
    """
    Returns the number of rows in the table
    """
    attached_leaves = self.getAttachedNodes(self.getColumns())
    return max([c.numCells() for c in attached_leaves])

  # TODO: This won't work with nested columns
  def refactorColumn(self, cur_colnm, new_colnm):
    """
    Changes the column name and its occurrences in formulas in the table.
    :param str cur_colnm: Current name of the column
    :param str new_colnm: New name of the column
    :returns list-of-str changed_columns:
    :raises ValueError: column name is unknown
    """
    def changeFormula(formula_statement):
      """
      Changes the formula by replacing occurrences of
      cur_colnm with new_colnm
      :param FormulaStatement formula_satement:
      :returns str/None: new formula or None
      """
      formula = formula_statement.getFormula()
      if cur_colnm in formula:
        return formula.replace(cur_colnm, new_colnm)
      else:
        return None

    column = self.columnFromName(cur_colnm)
    if column is None:
      raise ValueError("Column %s does not exist." % cur_colnm)
    column.setName(new_colnm)
    columns = self.getColumns(is_attached=False)
    changed_columns = []
    try:
      # Do the Columns
      for col in self.getFormulaColumns():
        new_formula = changeFormula(col.getFormulaStatementObject())
        if new_formula is not None:
          col.setFormula(new_formula)
          changed_columns.append(col.getName())
      # Handle Prologue
      new_formula = changeFormula(self.getPrologue())
      if new_formula is not None:
        self.setPrologue(new_formula)
        changed_columns.append(PROLOGUE_NAME)
      # Handle Epilogue
      new_formula = changeFormula(self.getEpilogue())
      if new_formula is not None:
        self.setEpilogue(new_formula)
        changed_columns.append(PROLOGUE_NAME)
    except Exception as err:
      msg = '''Changing column name from %s to %s.
Encountered error %s.
Changed formulas in columns %s.''' % (cur_colnm, new_colnm,
    str(err), ' '.join(changed_columns))
    return changed_columns

  @staticmethod
  def rowIndexFromName(name):
    """
    Returns the row index for the row name
    """
    return int(name) - 1

  def renameColumn(self, column, proposed_name):
    """
    Renames the column, checking for a duplicate
    :param column: column object
    :param proposed_name: str, proposed name
    :return: Boolean indicating success or failure
    """
    names = [c.getName(is_global_name=False) for c in self.getChildren()]
    bool_test = all([name != proposed_name for name in names])
    if bool_test:
      column.setName(proposed_name)
    return bool_test

  def renameRow(self, row_index, proposed_name):
    """
    Renames the row so that it is an integer value
    that creates the row ordering desired.
    Handles subtrees by making their name columns
    the same length as the root.
    :param row_index: index of the row to change
    :param proposed_name: string of a number
    """
    root = self.getRoot()
    name_column = root.columnFromName(NAME_COLUMN_STR)
    names = name_column.getCells()
    try:
      names[row_index] = str(proposed_name)
    except:
      import pdb; pdb.set_trace()
    try:
      float_names = [float(x) for x in names]
    except:
      import pdb; pdb.set_trace()
    sel_index = np.argsort(float_names)
    new_names = Table._rowNamesFromSize(len(names))
    for column in self.getChildren(is_recursive=True):
      if Table.isNameColumn(column):
        column.replaceCells(list(new_names))
    self._updateNameColumn()
    # Update the order of values in each column
    for column in self.getLeaves(is_attached=True):
      if not Table.isNameColumn(column):
        data = column.getCells()
        new_data = [data[n] for n in sel_index]
        column.replaceCells(new_data)

  def setNamespace(self, namespace):
    self._namespace = namespace
 
  def setIsEvaluateFormulas(self, setting):
    self._is_evaluate_formulas = setting

  def setEpilogue(self, epilogue_formula):
    """
    :param str epilogue_formula: New value for the Epilogue formula
    """
    self._epilogue = FormulaStatement(epilogue_formula, EPILOGUE_NAME)
    return self._epilogue.do()

  def setPrologue(self, prologue_formula):
    """
    :param str prologue_formula: New value for the Prologue formula
    """
    self._prologue = FormulaStatement(prologue_formula, PROLOGUE_NAME)
    return self._prologue.do()
        
  def tableFromName(self, name, is_relative=True):
    """
    Finds the table with the specified name or None.
    Note that Columns must be leaves in the Tree.
    :param name: name of the column
    :return: column - column object or None if not found
    """
    leaf = self.childFromName(name, is_relative=is_relative)
    if Table.isTable(leaf):
      return leaf

  def trimRows(self):
    """
    Removes all consequative rows at the end of the table
    that have None values in the data columns
    """
    num_rows = self.numRows()
    row_indexes = range(num_rows)
    row_indexes.sort(reverse=True)
    for index in row_indexes:
      row = self.getRow(row_index=index)
      # Delete all of the name columns
      for colnm in row.keys():
        column = self.columnFromName(colnm, is_relative=False)
        if column is None:
          import pdb; pdb.set_trace()
        if Table.isNameColumn(column):
          del row[column.getName()]
      delete_row = True
      for name in row.keys():
        column = self.columnFromName(name)
        if not isNull(row[name]):
          delete_row = False
      if delete_row:
        self.deleteRows([index])
      else:
        break

  def updateCell(self, value, row_index, column_id):
    """
    Changes the value of the identified cell
    :param obj value: new value for the cell
    :param int row_index: 0-based index of the row
    :param int/str column_id: 0-based index of the column or its name
    """
    if isinstance(column_id, int):
      column = self.columnFromIndex(column_id)
    else:
      column = self.childFromName(column_id, is_relative=False)
    column.updateCell(value, row_index)

  def updateColumn(self, column, cells):
    """
    Replaces the cells in the column with those provided
    :param column: column to update
    :param cells: cells to change
    """
    column.addCells(cells, replace=True)
    self.adjustColumnLength()
    self._validateTable()

  def updateRow(self, row, index):
    """
    Updates the row in place. Only changes values
    Assigns the value of the NAME_COLUMN
    that are specified in row.
    :param row: Row
    :param index: index of row to change
    """
    row[NAME_COLUMN_STR] = Table._rowNameFromIndex(index)
    for name in row:
      column = self.columnFromName(name)
      if not Table.isNameColumn(column):
        column.updateCell(row[name], index)
    self.adjustColumnLength()

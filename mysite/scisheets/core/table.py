'''
  Implements the table class for SciSheets.
'''

from mysite import settings
import mysite.helpers.util as ut
from mysite.helpers.data_capture import DataCapture
from mysite.helpers.versioned_file import VersionedFile
from helpers.formula_statement import FormulaStatement
from column import Column
from column_container import ColumnContainer
from table_evaluator import TableEvaluator
import errors as er
import column as cl
import numpy as np
import os
import pandas as pd

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

  def getSerializationDict(self, class_variable):
    """
    :param str class_variable: key to use for the class name
    :return dict: dictionary encoding the Table object and its columns
    """
    serialization_dict = {}
    serialization_dict[class_variable] = str(self.__class__)
    more_dict = {
        "_name": self.getName(),
        "_prologue_formula": self.getPrologue().getFormula(),
        "_epilogue_formula": self.getEpilogue().getFormula(),
        "_is_evaluate_formulas": self.getIsEvaluateFormulas(),
        "_filepath": self.getFilepath(),
        }
    serialization_dict.update(more_dict)
    _columns = []
    for column in self.getColumns():
      _columns.append(column.getSerializationDict(class_variable))
    serialization_dict["_columns"] = _columns
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
    column_dicts = serialization_dict["_columns"]
    for column_dict in column_dicts:
      new_column = Column.deserialize(column_dict)
      table.addColumn(new_column)
    return table


  # The following methods are used in debugging

  def d(self):
    return [(c.getName(), c.getCells()) for c in self._columns]

  def f(self):
    return [(c.getName(), c.getFormula()) for c in self._columns]

  def setCapture(self, filename, data):
    dc = DataCapture(filename)
    dc.setData(data)

  def getCapture(self, filename):
    dc = DataCapture(filename)
    return dc.getData()
 
  def getIsEvaluateFormulas(self):
    return self._is_evaluate_formulas
  
  # Internal and other methods

  def _updateNameColumn(self):
    """
    Changes the cells in the name column to be consecutive ints.
    """
    names = []
    if len(self._columns) > 1:
      num_cells = self._columns[NAME_COLUMN_IDX + 1].numCells()
    else:
      num_cells = self._columns[NAME_COLUMN_IDX].numCells()
    if len(self._columns) > 1:
      for row_num in range(num_cells):
        names.append(Table._rowNameFromIndex(row_num))
      self._columns[NAME_COLUMN_IDX].addCells(names, replace=True)

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
    return self._columns[NAME_COLUMN_IDX + 1:]

  def getData(self):
    """
    Returns the data values in an array ordered by column index
    """
    return [c.getCells() for c in self._columns]

  def getEpilogue(self):
    """
    :return FormulaStatement:
    """
    return self._epilogue

  def getFormulaColumns(self):
    """
    :return list-of-Column:
    """
    result = [c for c in self._columns if c.getFormula() is not None]
    return result

  def getRow(self, index=None):
    """
    :param index: row desired
           if None, then a row of None is returned
    :return: Row object
    """
    row = Row()
    for column in self._columns:
      if index is None:
        if column.isFloats():
          row[column.getName()] = np.nan  # pylint: disable=E1101
        else:
          row[column.getName()] = None
      else:
        row[column.getName()] = column.getCells()[index]
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
    for column in self._columns:
      adj_rows = num_rows - column.numCells()
      if adj_rows > 0:
        if column.isFloats():
          column.addCells(np.repeat(np.nan, adj_rows))  # pylint:disable=E1101
        else:
          column.addCells(np.repeat(none_array, adj_rows))
    self._updateNameColumn()

  def _validateTable(self):
    """
    Checks that the table is internally consistent
    Verify that there is at least one column
    """
    if len(self._columns) < 1:
      raise er.InternalError("Table %s has no columns." % self._name)
    # Verify that all columns have the same number of cells
    num_rows = len(self.columnFromName(NAME_COLUMN_STR).getCells())
    for column in self._columns:
      if  column.numCells() != num_rows:
        import pdb; pdb.set_trace()
        msg = "In Table %s, Column %s differs in its number of rows." \
            % (self.getName(), column.getName())
        raise er.InternalError(msg)
    # Verify that the first Column is the Name Column
    if self._columns[0].getName() != NAME_COLUMN_STR:
      msg = "In Table %s, first column is not 'row' column" % self.getName()
      raise er.InternalError(msg)
    # Verify that names are unique
    names = []
    for col in self._columns:
      names.append(col.getName())
    if len(names) != len(set(names)):
      raise er.DuplicateColumnName("Duplicate names in Table %s"
          % self.getName())
    # Verify the sequence of row names
    for nrow in range(self.numRows()):
      expected_row_name = Table._rowNameFromIndex(nrow)
      actual_row_name = self._columns[NAME_COLUMN_IDX].getCells()[nrow]
      if actual_row_name != expected_row_name:
        import pdb; pdb.set_trace()
        msg = "In Table %s, invalid row name at index %d: %s" % \
                (self.getName(), nrow, actual_row_name)
        raise er.InternalError(msg)
    # Verify that the columns have the corrent table
    for column in self.getColumns():
      if not column.getTable() == self:
        raise er.InternalError("Column %s in Table %s does not have correct parent"  \
             % (column.getName(), self.getName()))
 

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
    is_ok = all([c.getName() != column.getName() for c in self._columns])
    if not is_ok:
      error = "**%s is a duplicate name" % column.getName()
      return error
    else:
      error = cl.Column.isPermittedName(column.getName())
      if error is not None:
        return error
    if index is None:
      index = len(self._columns)
    # Handle the different cases of adding a column
    # Case 1: NameColumn
    if self.numColumns() == 0:
      self.insertColumn(column, index=index)
      column.setTable(self)
    # Case 2: First column after name column
    elif self.numColumns() == 1:
      self.insertColumn(column, index=index)
      column.setTable(self)
      self._updateNameColumn()
      self._validateTable()
    # Case 3: Subsequent columns
    else:
      self.insertColumn(column, index=index)
      column.setTable(self)
      self.adjustColumnLength()
      self._validateTable()

  def addRow(self, row, ext_index=None):
    """
    :param row: Row to add
    :param ext_index: index where Row is added, may be a float
                       if None, then appended
    """
    # Determine the actual desired name
    if ext_index is None:
      proposed_name = Table._rowNameFromIndex(self.numRows())
    else:
      proposed_name = Table._rowNameFromIndex(ext_index)
    # Assign values to the cells in the Row
    for column in self._columns:
      cur_name = column.getName()
      if cur_name in row:
        column.insertCell(row[cur_name])
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
      instance = Table(self.getName())
    # Copy everything required from inherited classes
    super(Table, self).copy(instance=instance)
    # Set properties specific to this class
    instance.setPrologue(self.getPrologue().getFormula())
    instance.setEpilogue(self.getEpilogue().getFormula())
    instance.setIsEvaluateFormulas(self.getIsEvaluateFormulas())
    for column in self.getColumns():
      new_column = column.copy()
      instance.addColumn(new_column)
    return instance

  def deleteColumn(self, column):
    """
    Deletes a column from the table.
    :param column: column obj to delete
    """
    column.setTable(None)
    self.removeColumn(column)

  def deleteRows(self, indicies):
    """
    Deletes rows
    :param indicies: index of rows to delete
    """
    indicies.sort()
    indicies.reverse()
    for column in self._columns:
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
    return evaluator.evaluate(user_directory=user_directory)

  def isColumnPresent(self, column_name):
    """
    :param str column_name:
    :return bool: True if column is present
    """
    for column in self._columns:
      if column.getName() == column_name:
        return True
    return False

  def isEquivalent(self, other_table):
    """
    Checks that the tables have the same values of their properties,
    excluding the VersionedFile.
    :param Table other_table:
    :returns bool:
    """
    local_debug = False # Breaks on specifc reasons for non-equiv
    if not isinstance(other_table, Table)  \
        and not issubclass(Table, other_table.__class__):
      if local_debug:
        import pdb; pdb.set_trace()
      return False
    is_same_properties = (self.getName() == other_table.getName()) and  \
        (self.numColumns() == other_table.numColumns()) and  \
        (self.getPrologue().isEquivalent(other_table.getPrologue())) and  \
        (self.getEpilogue().isEquivalent(other_table.getEpilogue()))
    if not is_same_properties:
      if local_debug:
        import pdb; pdb.set_trace()
      return False
    for column in self._columns:
      other_column = other_table.columnFromName(column.getName())
      if other_column is None:
        if local_debug:
          import pdb; pdb.set_trace()
        return False
      if not column.isEquivalent(other_column):
        if local_debug:
          import pdb; pdb.set_trace()
        return False
    return True
   

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
    for ncol in range(self.numColumns()):
      column = self._columns[ncol]
      name = column.getName()
      if name in row.keys():
        column.insertCell(row[name], idx)
      else:
        column.insertCell(None, idx)
    self._updateNameColumn()

  def migrate(self, instance=None):
    """
    Handles older objects that lack some properties
    :param Table instance:
    :returns Table (or subclass of Table):
    """
    # Fix the current object
    if not '_namespace' in dir(self):
      self._namespace = {}
    if not '_prologue' in dir(self):
      self._prologue =  \
          self._formulaStatementFromFile(PROLOGUE_FILEPATH,
                                         PROLOGUE_NAME)
    if not '_epilogue' in dir(self):
      self._epilogue =  \
          self._formulaStatementFromFile(EPILOGUE_FILEPATH,
                                         EPILOGUE_NAME)
    if not "_is_evaluate_formulas" in dir(self):
      self._is_evaluate_formulas = True
    if not '_versioned_file' in dir(self):
      if '_filepath' in dir(self):
        self._versioned_file = VersionedFile(self._filepath,
            settings.SCISHEETS_USER_TBLDIR_BACKUP,
            settings.SCISHEETS_MAX_TABLE_VERSIONS)
      else:
        self._versioned_file = None
    # Copy the colunns to ensure that the class structures are updated
    for column in self.getColumns():
      index = self.indexFromColumn(column)
      new_column = column.migrate()
      self.deleteColumn(column)
      self.insertColumn(new_column, index)
    # Create an object if none is provided
    if instance is None:
      instance = Table(self.getName())
    # Do migration for all inherited classes
    instance = super(Table, self).migrate(instance=instance)
    # Copy the properties of this class
    return self.copy(instance=instance)

  def moveRow(self, index1, index2):
    """
    Moves the row at index1 to index2
    """
    row = self.getRow(index1)
    self.deleteRows([index1])
    self.insertRow(row, index2)
    self._updateNameColumn()

  def numRows(self):
    """
    Returns the number of rows in the table
    """
    return max([c.numCells() for c in self._columns])

  # TODO: Should check for exceptions and revert to a 
  #       previous version of the table if encounter an error
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
    columns = self.getColumns()
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
    names = [c.getName() for c in self.getColumns()]
    bool_test = all([name != proposed_name for name in names])
    if bool_test:
      column.setName(proposed_name)
    return bool_test

  def renameRow(self, row_index, proposed_name):
    """
    Renames the row so that it is an integer value
    that creates the row ordering desired.
    :param row_index: index of the row to change
    :param proposed_name: string of a number
    """
    name_column = self.getColumns()[NAME_COLUMN_IDX]
    names = name_column.getCells()
    try:
      names[row_index] = str(proposed_name)
    except:
      import pdb; pdb.set_trace()
    float_names = [float(x) for x in names]
    sel_index = np.argsort(float_names)
    new_names = Table._rowNamesFromSize(len(names))
    name_column.replaceCells(new_names)
    # Update the order of values in each column
    for column in self._columns:
      try:
        if column.getName() != NAME_COLUMN_STR:
          data = column.getCells()
          new_data = [data[n] for n in sel_index]
          column.replaceCells(new_data)
      except:
        import pdb; pdb.set_trace()

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

  def trimRows(self):
    """
    Removes all consequative rows at the end of the table
    that have None values in the data columns
    """
    num_rows = self.numRows()
    row_indxs = range(num_rows)
    row_indxs.sort(reverse=True)
    for index in row_indxs:
      row = self.getRow(index=index)
      del row[NAME_COLUMN_STR]
      delete_row = True
      for name in row.keys():
        column = self.columnFromName(name)
        if column.isFloats():
          if not np.isnan(row[name]):  # pylint: disable=E1101
            delete_row = False
        else:
          if row[name] is not None:
            delete_row = False
      if delete_row:
        self.deleteRows([index])
      else:
        break

  def updateCell(self, value, row_index, column_index):
    """
    Changes the value of the identified cell
    :param value: new value for the cell
    :param row_index: 0-based index of the row
    :param column_index: 0-based index of the column
    """
    column = self.columnFromIndex(column_index)
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
    for ncol in range(self.numColumns()):
      column = self._columns[ncol]
      name = column.getName()
      if name in row.keys():
        if name != NAME_COLUMN_STR:
          column.updateCell(row[name], index)

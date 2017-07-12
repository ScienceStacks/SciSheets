'''Tests for scisheets_views'''

from mysite import settings as st
from helpers_test import HelperHTTP, COLUMN_INDEX
import common_util.util as ut
from django.test import TestCase
from scisheets.core.table import Table
import scisheets.ui.dt_table as dt
from scisheets.core.helpers_test import TableFileHelper, TEST_DIR,  \
    compareTableData
from scisheets.core.helpers.api_util import readObjectFromFile, writeObjectToFile
import scisheets.core.helpers.cell_types as cell_types
import scisheets_views as sv
import json
import numpy as np
import os
import shutil

# Keys used inside the server
DICT_NAMES =  ["command", "target", "table_name",
    "row_index", "value", "column_name"]
# Parameter names in the Ajax call
AJAX_NAMES =  ["command", "target", "table",
    "row",       "value", "columnName" ]
NCOL = 3
NROW = 4
BASE_URL = "http://localhost:8000/scisheets/"
TABLE_PARAMS = [NCOL, NROW]
IGNORE_TEST = False


class TestScisheetsViews(TestCase):
 
  def setUp(self):
    self._helper_http = HelperHTTP()

  def _createBaseTable(self, params=TABLE_PARAMS):
    # Create the table
    # Output - response from command
    create_table_url = self._helper_http.createBaseURL(params=params)
    return self.client.get(create_table_url)

  def _getTableFromResponse(self, response):
    table_filepath = response.client.session[sv.TABLE_FILE_KEY]
    return readObjectFromFile(table_filepath)

  def _findColumnWithType(self, table, val):
    """
    :param Table table:
    :param object val:
    :return Column:
    Assumes that the columns are either str or a number
    """
    def notIsStrs(vals):
      return not cell_types.isStrs(vals)

    if cell_types.isStr(val):
      func = cell_types.isStrs
    else:
      func = notIsStrs
    for column in table.getColumns():
      if Table.isNameColumn(column):
        continue
      if func(column.getCells()):
        return column

  def _verifyResponse(self, response, checkSessionid=True):
    self.assertEqual(response.status_code, 200)
    if checkSessionid:
      self.assertTrue(response.cookies.has_key('sessionid'))
    expected_keys = ['column_hierarchy', 'response_schema', 
        'table_id', 'table_caption', 'data']
    self.assertTrue(response.context.keys().issuperset(expected_keys))
  
  def testSaveAndGetTable(self):
    if IGNORE_TEST:
       return
    request = self._helper_http.URL2Request(
        self._helper_http.createURL(count=1))  # a request
    self._helper_http.addSessionToRequest(request)
    self.assertEqual(sv.getTable(request), None)
    table = Table("test")
    sv.saveTable(request, table)
    self.assertTrue(request.session.has_key(sv.TABLE_FILE_KEY))
    new_table = sv.getTable(request)
    self.assertEqual(new_table.getName(is_global_name=False), 
        table.getName(is_global_name=False))

  def testRandomTable(self):
    if IGNORE_TEST:
       return
    # Test creation of the initial random table
    response = self._createBaseTable()
    self._verifyResponse(response)

  def testCommandReload(self):
    if IGNORE_TEST:
       return
    self._createBaseTable()
    # Do the refresh
    refresh_url = self._helper_http.createBaseURL()
    response = self.client.get(refresh_url)
    self._verifyResponse(response, checkSessionid=False)

  def _testCommandCellUpdate(self, row_index, val, check_value=True,
      table=None, column_name=None, column_index=None, valid=True):
    if table is None:
      response = self._createBaseTable()
      table = self._getTableFromResponse(response)
    if column_index is not None:
      column = table.columnFromIndex(column_index)
      column_name = column.getName(is_global_name=False)
    if (column_name is None):
      column = self._findColumnWithType(table, val)
      column_name = column.getName()
    # Do the cell update
    create_table_url = self._helper_http.createBaseURL()
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Cell'
    ajax_cmd['command'] = 'Update'
    ajax_cmd['row'] = table._rowNameFromIndex(row_index)
    ajax_cmd['columnName'] = column_name
    ajax_cmd['value'] = val
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=create_table_url)
    response = self.client.get(command_url)
    table = self._getTableFromResponse(response)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("data"))
    if valid:
      self.assertEqual(content["data"], "OK")
      if check_value:
        self.assertEqual(table.getCell(row_index, column_name), val)
    else:
      self.assertNotEqual(content["data"], "OK")
    return table

  def _findColumnWithType(self, table, val):
    """
    :param Table table:
    :param object val:
    :return Column:
    Assumes that the columns are either str or a number
    """
    def notIsStrs(vals):
      return not cell_types.isStrs(vals)

    if cell_types.isStr(val):
      func = cell_types.isStrs
    else:
      func = notIsStrs
    for column in table.getColumns():
      if Table.isNameColumn(column):
        continue
      if func(column.getCells()):
        return column

  def testCommandCellUpdate(self):
    if IGNORE_TEST:
       return
    row_index = NROW - 1
    self._testCommandCellUpdate(row_index, 9999)
    self._testCommandCellUpdate(row_index, "aaa")
    self._testCommandCellUpdate(row_index, "aaa bb")

  def testCommandCellUpdateWithColumnListData(self):
    if IGNORE_TEST:
       return
    row_index = NROW - 1
    response = self._createBaseTable()
    table = self._getTableFromResponse(response)
    column = table.columnFromIndex(1)
    column_name = column.getName()
    table.updateCell([1,2,3], row_index, column_name)
    writeObjectToFile(table)
    self._testCommandCellUpdate(row_index, 2, valid=False, 
        table=table, column_name=column_name)

  def testCommandCellUpdateWithValueAsList(self):
    if IGNORE_TEST:
       return
    row_index = NROW - 1
    value = [1, 2]
    column_index = 1
    table = self._testCommandCellUpdate(row_index, value, 
        column_index=column_index, check_value=False)
    self.assertEqual(table.getCell(row_index, column_index),
        str(value))

  def _getTableFromResponse(self, response):
    table_filepath = response.client.session[sv.TABLE_FILE_KEY]
    return readObjectFromFile(table_filepath)

  def _testCommandColumnDelete(self, base_url):
    # Tests for command delete with a given base_url to consider the
    # two use cases of the initial table and a reload
    # Input - base_url - base URL used in the request
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    # Do the column delete
    column = table.columnFromIndex(COLUMN_INDEX)
    column_name = column.getName(is_global_name=False)
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Column'
    ajax_cmd['command'] = 'Delete'
    ajax_cmd['column_name'] = column_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=base_url)
    response = self.client.get(command_url)
    # Check the table
    table = self._getTableFromResponse(response)
    columns = table.getColumns()
    self.assertEqual(len(columns), NCOL)  # Added the 'row' column
    self.assertEqual(columns[0].numCells(), NROW)

  def testCommandColumnDelete(self):
    if IGNORE_TEST:
       return
    self._testCommandColumnDelete(BASE_URL)

  def _testCommandColumnRename(self, 
    base_url, 
    new_name, 
    is_successful_outcome,
    command='Rename'):
    # Tests for command column rename with a given base_url to consider the
    # two use cases of the initial table and a reload
    # Input - base_url - base URL used in the request
    #         new_name - new column name
    #         is_successful_outcome - Boolean whether rename is successful
    #         command - command issued, either Rename or Refactor
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    # Do the cell update
    column_index = 2
    column = table.columnFromIndex(column_index)
    column_name = column.getName(is_global_name=False)
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Column'
    ajax_cmd['command'] = command
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = new_name.replace(' ', '+')
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=base_url)
    response = self.client.get(command_url)
    returned_data = json.loads(response.getvalue())
    # Check the table
    if not is_successful_outcome:
      self.assertFalse(returned_data['success'])
    else:
      self.assertTrue(returned_data['success'])
      table = self._getTableFromResponse(response)
      columns = table.getColumns()
      self.assertEqual(len(columns), NCOL+1)  # Added the 'row' column
      self.assertEqual(table.getNameColumn().numCells(), NROW)
      self.assertEqual(
          columns[column_index].getName(is_global_name=False), 
          new_name)

  def testCommandColumnRename(self):
    if IGNORE_TEST:
       return
    new_name = 'row'  # duplicate name
    self._testCommandColumnRename(BASE_URL, new_name, False)
    NEW_NAME = "New_Column"
    self._testCommandColumnRename(BASE_URL, NEW_NAME, True)

  def _refactor(self, column_name, refactor_name, isValid):
    """
    Changes the name in column 1 and the formula formula in column 2
    to test Refactor
    :param str column_name: name of the column to be refactored
    :param str refactor_name: new name for column 1
    :param bool isValid: is a valid formula
    """
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    # Change the formula
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['columnName'] =  column_name
    ajax_cmd['args[]'] = refactor_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    # Refactor the name 
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Refactor"
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = refactor_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    # Check the response
    self.assertTrue(content["success"] == isValid)

  def testCommandColumnRefactorName(self):
    if IGNORE_TEST:
       return
    new_name = 'row'  # duplicate name
    self._testCommandColumnRename(BASE_URL, new_name, False)
    new_name = "New_Column"
    self._testCommandColumnRename(BASE_URL, new_name, True, command="Refactor")

  def testCommandColumnRefactorFormula(self):
    if IGNORE_TEST:
      return
    column_name = "Col_0"
    refactor_name = "NewColumn"
    self._refactor(column_name, refactor_name, True)

  def _numRows(self, table_data):
    """
    Determines the number of rows from the getData() dict
    :return int:
    """
    keys = table_data.keys()
    key = keys[0]
    return len(table_data[key])

  def testCommandRowMove(self):
    if IGNORE_TEST:
       return
    # Tests row renaming by moving the first row
    # to the end of the table
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    num_rows = self._numRows(table_data)
    num_columns = table.numColumns()
    rplIdx = range(num_rows)
    del rplIdx[0]
    rplIdx.append(0)
    new_row_name = table._rowNameFromIndex(table.numRows())
    # Do the cell update
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = 'Move'
    ajax_cmd['row'] = 1
    ajax_cmd['args[]'] = new_row_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numRows(), num_rows)
    self.assertEqual(new_table.numColumns(), num_columns)
    new_table_data = new_table.getData()
    for name in table_data.keys():
      expected_array = np.array([table_data[name][n] for n in rplIdx])
      b = (new_table_data[name] == expected_array).all()
      self.assertTrue(b)

  def testCommandRowDelete(self):
    if IGNORE_TEST:
       return
    ROW_IDX = 1
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    num_rows = self._numRows(table_data)
    num_columns = table.numColumns()
    rplIdx = range(num_rows)
    del rplIdx[ROW_IDX - 1]
    # Do the cell update
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = 'Delete'
    ajax_cmd['row'] = ROW_IDX
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numRows(), num_rows - 1)
    self.assertEqual(new_table.numColumns(), num_columns)
    new_table_data = new_table.getData()
    for name in table_data:
      expected_array = np.array([table_data[name][n] for n in rplIdx])
      b = (new_table_data[name] == expected_array).all()
      self.assertTrue(b)

  def _addRow(self, command, cur_idx, new_idx):
    # Inputs: command - string of command to issue
    #         cur_idx - index of the current row
    #         new_idx - index of the new row
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    num_rows = table.numRows()
    num_columns = table.numColumns()
    row_name = table._rowNameFromIndex(cur_idx)
    # Do the cell update
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = command
    ajax_cmd['row'] = row_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numRows(), num_rows + 1)
    self.assertEqual(new_table.numColumns(), num_columns)
    # New row should have all None values (or np.nan for numbers)
    new_row = new_table.getRow(new_idx)
    b = True
    for k in new_row.keys():
      if k != 'row':
        column = new_table.columnFromName(k)
        if column.isFloats():
          b = b and np.isnan(new_row[k])
        else:
          b = b and (new_row[k] is None)
    self.assertTrue(b)  # New row should be 'None'

  def testCommandRowInsert(self):
    if IGNORE_TEST:
       return
    self._addRow("Insert", 0, 0)
    self._addRow("Insert", NROW - 1, NROW - 1)
    self._addRow("Insert", 2, 2)

  def testCommandRowAppend(self):
    if IGNORE_TEST:
       return
    self._addRow("Append", 0, 1)
    self._addRow("Append", NROW - 1, NROW)
    self._addRow("Append", 2, 3)

  def _addColumn(self, command, cur_idx, new_idx):
    # Inputs: command - string of command to issue
    #         cur_idx - index of the current column
    #         new_idx - index of the new column
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    column = table.columnFromIndex(cur_idx)
    column_name = column.getName(is_global_name=False)
    num_rows = table.numRows()
    num_columns = table.numColumns()
    # Do the cell update
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Column'
    ajax_cmd['command'] = command
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = 'Yet_Another_Column'
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numColumns(), num_columns + 1)
    self.assertEqual(new_table.numRows(), num_rows)
    # New column should have all None values
    new_column = new_table.getColumns()[new_idx]
    self.assertTrue(new_column.numCells(), num_rows)
    b = all([np.isnan(x) for x in new_column.getCells()])
    if not b:
      import pdb; pdb.set_trace()
    self.assertTrue(b)

  def testCommandColumnInsert(self):
    if IGNORE_TEST:
       return
    self._addColumn("Insert", 1, 1)
    self._addColumn("Insert", 2, 2)
    self._addColumn("Insert", NCOL, NCOL)

  def testCommandColumnAppend(self):
    if IGNORE_TEST:
       return
    self._addColumn("Append", 1, 2)
    self._addColumn("Append", 2, 3)
    self._addColumn("Append", NCOL, NCOL+1)

  def _moveColumn(self, column_idx_to_move, dest_column_name):
    # Inputs: column_idx_to_move - index of column to be moved
    #         dest_column_name - name of the dest column after
    #         which the column is to be moved
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    column = table.columnFromIndex(column_idx_to_move)
    column_name = column.getName(is_global_name=False)
    num_rows = table.numRows()
    num_columns = table.numColumns()
    moved_column = table.columnFromIndex(column_idx_to_move)
    dest_column = table.columnFromName(dest_column_name)
    expected_index = table.indexFromColumn(dest_column)
    # Do the cell update
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Move"
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = dest_column_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numColumns(), num_columns)
    self.assertEqual(new_table.numRows(), num_rows)
    # New column should have all None values
    column = new_table.getColumns()[expected_index]
    self.assertEqual(column.getName(is_global_name=False), 
       moved_column.getName(is_global_name=False))
    b = all([column.getCells()[n] == moved_column.getCells()[n] 
             for n in range(column.numCells())])
    if not b:
      import pdb; pdb.set_trace()
    self.assertTrue(b)
  
  def _makeColumnName(self, index):
    return "Col_%d" % index

  def testCommandColumnMove(self):
    if IGNORE_TEST:
       return
    # The column names are "row", "Col_0", ...
    self._moveColumn(1, self._makeColumnName(NCOL-1))  # Make it the last column

  def _formulaColumn(self, column_idx, formula, isValid):
    # Inputs: column_idx - index of column whose formula is changed
    #         formula - new formula for column
    #         isValid - is a valid formula
    # Assumes that formula ony changes column_idx
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    old_table = table.copy()
    column = table.columnFromIndex(column_idx)
    column_name = column.getName(is_global_name=False)
    old_formula = column.getFormula()
    # Reset the formula
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = formula
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    # Check the table
    new_table = self._getTableFromResponse(response)
    new_column = new_table.childFromName(column_name, is_relative=False)
    if isValid:
      self.assertTrue(content["success"])
      self.assertEqual(formula, new_column.getFormula())
    else:
      self.assertFalse(content["success"])
      self.assertEqual(formula, new_column.getFormula())
    # Check the columns
    self.assertTrue(compareTableData(old_table, 
                                     new_table, 
                                     excludes=[column_idx]))

  def testCommandColumnFormula(self):
    if IGNORE_TEST:
       return
    self._formulaColumn(NCOL - 1, "np.sin(2.3)", True)  # Valid formula
    self._formulaColumn(NCOL - 1, "np.sin(2.3", False)  # Invalid formula

  def _evaluateTable(self, formula, isValid, col_idx=NCOL-1):
    # Inputs: formula - new formula for column
    #         isValid - is a valid formula
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    column = table.columnFromIndex(col_idx)
    column_name = column.getName(is_global_name=False)
    # Change the formula
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = formula
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    # Check the table
    new_table = self._getTableFromResponse(response)
    error = new_table.evaluate(user_directory=TEST_DIR)
    if isValid:
      self.assertTrue(content["success"])
    else:
      self.assertFalse(content["success"])

  def testTableEvaluate(self):
    if IGNORE_TEST:
       return
    self._evaluateTable("np.sin(3.2)", True)  # Valid formula
    self._evaluateTable("range(1000)", True)  # Test large
    formula = "Col_2 = np.sin(np.array(range(10), dtype=float));B =  Col_1**3"
    self._evaluateTable(formula, True)  # Compound formula
    self._evaluateTable("np.sin(x)", False)  # Invalid formula

  def testTableExport(self):
    if IGNORE_TEST:
       return
    # Populate the table with a couple of formulas
    FORMULA = "range(10)"
    FUNC_NAME = "ss_export_test"
    self._evaluateTable(FORMULA, True)
    # Do the export
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Sheet"
    ajax_cmd['command'] = "Export"
    inputs = "Col_1"
    outputs = "Col_%d, Col_%d" % (NCOL-1, NCOL-2)
    arg_list = [FUNC_NAME, inputs, outputs]
    ajax_cmd['args[]'] = arg_list
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))

  def _tableTrim(self, row_idx, expected_number_rows):
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    row_name = table._rowNameFromIndex(row_idx)
    # Add the row
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = 'Append'
    ajax_cmd['row'] = row_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Do the trim
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['columnName'] = table.getName()
    ajax_cmd['command'] = 'Trim'
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numRows(), expected_number_rows)

  def testTableTrim(self):
    if IGNORE_TEST:
       return
    self._tableTrim(0, NROW+1)
    self._tableTrim(NROW, NROW)

  def _tableRename(self, new_name, is_valid_name):
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    old_name = table.getName(is_global_name=False)
    # Rename the table
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'Rename'
    ajax_cmd['columnName'] = table.getName()
    ajax_cmd['args[]'] = new_name
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the result
    new_table = self._getTableFromResponse(response)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    if is_valid_name:
      content = json.loads(response.content)
      if not content["success"]:
        import pdb; pdb.set_trace()
      self.assertTrue(content["success"])
      self.assertEqual(new_table.getName(is_global_name=False), 
          new_name)
    else:
      self.assertFalse(content["success"])
      self.assertEqual(new_table.getName(is_global_name=False), 
          old_name)

  def testTableRename(self):
    if IGNORE_TEST:
       return
    self._tableRename("valid_name", True)
    self._tableRename("invalid_name!", False)

  def testTableListSheetFiles(self):
    if IGNORE_TEST:
       return
    filename = "dummy"
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    helper.create()
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Sheet'
    ajax_cmd['command'] = 'ListSheetFiles'
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])
    self.assertTrue("data" in content)
    self.assertTrue(filename in content["data"])
    helper.destroy()

  def testTableOpenSheetFiles(self):
    if IGNORE_TEST:
       return
    filename = "dummy"
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    helper.create()
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Sheet'
    ajax_cmd['command'] = 'OpenSheetFile'
    ajax_cmd['args[]'] = filename
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])
    helper.destroy()

  def _tableSave(self, filename):
    """
    Saves a table to file
    :param filename: - file name to save to
    """
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Sheet'
    ajax_cmd['command'] = 'SaveAs'
    ajax_cmd['columnName'] = table.getName()
    ajax_cmd['args[]'] = filename
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])

  def testTableSave(self):
    if IGNORE_TEST:
      return
    filename = "dummy"
    _ = self._createBaseTable()
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    helper.create()
    self._tableSave(filename)
    helper.destroy()

  def testTableDelete(self):
    if IGNORE_TEST:
       return
    filename = "dummy"
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    _ = self._createBaseTable()
    helper.create()
    self._tableSave(filename)
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Sheet'
    ajax_cmd['command'] = 'Delete'
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])
    self.assertTrue(TableFileHelper.doesFilepathExist(
        st.SCISHEETS_DEFAULT_TABLEFILE))
    #helper.destroy()

  def testTableNew(self):
    if IGNORE_TEST:
       return
    filename = st.SCISHEETS_DEFAULT_TABLEFILE
    _ = self._createBaseTable()
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = 'Sheet'
    ajax_cmd['command'] = 'New'
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])
    self.assertTrue(TableFileHelper.doesFilepathExist(
        st.SCISHEETS_DEFAULT_TABLEFILE))

  def testHierarchicalTable(self):
    if IGNORE_TEST:
       return
    base_response = self._createBaseTable(params=[-NCOL, NROW])
    table = self._getTableFromResponse(base_response)
    self.assertEqual(table.numRows(), NROW)
    for col in table.getDataColumns():
      self.assertEqual(len(col.getCells()), NROW)

  def testFormulaRowAddition(self):
    if IGNORE_TEST:
       return
    column_idx = 1
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    column = table.columnFromIndex(column_idx)
    column_name = column.getName(is_global_name=False)
    # Change the formula
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['columnName'] = column_name
    num_rows = 2*NROW
    ajax_cmd['args[]'] = "range(%d)" % num_rows
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    # Check the table
    table = self._getTableFromResponse(response)
    error = table.evaluate(user_directory=TEST_DIR)
    self.assertTrue(content["success"])
    self.assertEqual(table.numRows(), num_rows)

  def _setFormula(self, table, formula, column_idx):
    """
    Sets the formula for the column index
    :param Table table:
    :param str formula:
    :param int column_idx
    :return HTTP response:
    """
    column = table.columnFromIndex(column_idx)
    column_name = column.getName(is_global_name=False)
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = formula
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    if not content["success"]:
      import pdb; pdb.set_trace()
    self.assertTrue(content["success"])
    #table = self._getTableFromResponse(response)
    return response

  def testTableWithLists(self):
    if IGNORE_TEST:
       return
    nrow = NROW + 1
    ncol = 4
    formula_columns = [3, 2]
    formula1 = '''xx = range(1,%d)
Col_2 = []
for x in xx:
  Col_2.append(range(x))
''' % nrow
    formula2 = """Col_1 = []
for x in Col_2:
  Col_1.append(np.average(x))
"""
    base_response = self._createBaseTable(params=[NROW, ncol])
    old_table = self._getTableFromResponse(base_response)
    # Change the first formula
    response = self._setFormula(old_table, formula1, formula_columns[0])
    # Change the second formula
    response = self._setFormula(old_table, formula2, formula_columns[1])
    # Check the table
    new_table = self._getTableFromResponse(response)
    error = new_table.evaluate(user_directory=TEST_DIR)
    self.assertEqual(new_table.numColumns(), old_table.numColumns())
    self.assertTrue(compareTableData(old_table, new_table, excludes=formula_columns))
    val = new_table.getColumns()[formula_columns[1]].getCells()[1]
    self.assertEqual(val, 0.5)

  def testImportExcelToTable(self):
    if IGNORE_TEST:
       return
    column_idx = 1
    filepath = os.path.join(TEST_DIR, 'RawData.xlsx')
    formula = "a = importExcelToTable(s, '%s')" % filepath
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    column = table.columnFromIndex(column_idx)
    column_name = column.getName(is_global_name=False)
    # Reset the formula
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = formula
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    self.assertTrue(content["success"])

  def _submitCommand(self, table, target, command, colidx, args):
    """
    Submits the command and checks the response. Returns the table.
    :param Table table:
    :param str target:
    :param str command:
    :param int colidx:
    :param str args:
    :return Table table:
    """
    column = table.columnFromIndex(colidx)
    column_name = column.getName(is_global_name=False)
    ajax_cmd = self._helper_http.ajaxCommandFactory()
    ajax_cmd['target'] = target
    ajax_cmd['command'] = command
    ajax_cmd['columnName'] = column_name
    ajax_cmd['args[]'] = args
    command_url = self._helper_http.createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    table = self._getTableFromResponse(response)
    return table

  # TODO: Complete test for Undo. Verify that all changes
  # are undone - value, column, table
  def _testUndoTable(self, formula):
    """
    :param str formula:
    :return Table:
    """
    colidx = 1
    # Inputs: formula - new formula for column
    base_response = self._createBaseTable()
    old_table = self._getTableFromResponse(base_response)
    column = old_table.columnFromIndex(colidx)
    self.assertIsNone(column.getFormula())
    # Change the formula
    changed_table = self._submitCommand(old_table, "Column", "Formula", colidx, formula)
    column = changed_table.columnFromIndex(colidx)
    self.assertEqual(column.getFormula(), formula)
    # Undo the change
    undone_table = self._submitCommand(changed_table, "Sheet", "Undo", colidx, "")
    column = undone_table.columnFromIndex(colidx)
    self.assertIsNone(column.getFormula())
    self.assertTrue(compareTableData(old_table, undone_table))
    return undone_table

  def testUndoTable(self):
    if IGNORE_TEST:
       return
    formula = "sin(4)"
    self._testUndoTable(formula)

  def testRedoTable(self):
    if IGNORE_TEST:
       return
    colidx = 1
    formula = "sin(4)"
    table = self._testUndoTable(formula)
    undone_table = self._submitCommand(table, "Sheet", "Redo", colidx, "")
    changed_table = self._submitCommand(undone_table, "Column", "Formula", colidx, formula)
    column = changed_table.columnFromIndex(colidx)
    self.assertEqual(column.getFormula(), formula)

  def _setPrologueEpilogue(self, formula, is_valid):
    """
    Sets the prologue and epilogue
    :param str formula:
    :param bool is_valid:
    :return HTTP response:
    """
    for command in ["Prologue", "Epilogue"]:
      base_response = self._createBaseTable()
      table = self._getTableFromResponse(base_response)
      ajax_cmd = self._helper_http.ajaxCommandFactory()
      ajax_cmd['target'] = "Table"
      ajax_cmd['command'] = command
      ajax_cmd['columnName'] = table.getName()
      ajax_cmd['args[]'] = formula
      command_url = self._helper_http.createURLFromAjaxCommand(
          ajax_cmd, address=BASE_URL)
      response = self.client.get(command_url)
      content = json.loads(response.content)
      self.assertTrue(content.has_key("success"))
      self.assertEqual(content["success"], is_valid)

  def testPrologueEpilogue(self):
    if IGNORE_TEST:
       return
    self._setPrologueEpilogue("import pdb", True)
    self._setPrologueEpilogue("impor pdb", False)


if __name__ == '__main__':
    unittest.main()

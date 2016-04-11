'''Tests for scisheets_views'''

from mysite import settings as st
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from ..core.table import Table
from ..core.helpers_test import TableFileHelper
from ..core.helpers.api_util import getTableFromFile, writeTableToFile
import json
import mysite.helpers.util as ut
import scisheets_views as sv
import os
import numpy as np

# Keys used inside the server
DICT_NAMES =  ["command", "target", "table_name", "column_index", "row_index", "value"]
# Parameter names in the Ajax call
AJAX_NAMES =  ["command", "target", "table",      "column",       "row",       "value"]
NCOL = 3
NROW = 4
BASE_URL = "http://localhost:8000/scisheets/"
TABLE_PARAMS = [NCOL, NROW]




class TestScisheetsViews(TestCase):
 
  def setUp(self):
    self.factory = RequestFactory()
  
  ''' Helper Methods '''

  def _addSessionToRequest(self, request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

  def _ajaxCommandFactory(self):
    TARGET = 'Cell'
    COMMAND = 'Update'
    VALUE = 'XXX'
    ROW_INDEX = 1
    COLUMN_INDEX = 3
    TABLE_NAME = 'XYZ'
    ajax_cmd = {}
    ajax_cmd['target'] = TARGET
    ajax_cmd['command'] = COMMAND
    ajax_cmd['value'] = VALUE
    ajax_cmd['row'] = ROW_INDEX
    ajax_cmd['column'] = COLUMN_INDEX
    ajax_cmd['table'] = TABLE_NAME
    ajax_cmd['args[]'] = None
    return ajax_cmd

  def _createBaseTable(self):
    # Create the table
    # Output - response from command
    create_table_url = self._createBaseURL(params=TABLE_PARAMS)
    return self.client.get(create_table_url)

  def _createBaseURL(self, params=None):
    # Creates the base URL to construct a table
    # Input: params
    #         0 - number of columns
    #         1 - number of rows
    # Output: URL
    if params is None:
      client_url = BASE_URL
    else:
      ncol = params[0]
      nrow = params[1]
      client_url = "%s%d/%d/" % (BASE_URL, ncol, nrow)
    return client_url

  def _createURL(self, address="dummy", count=None, values=None, names=None):
    # Input: count - number of variables
    #        names - variable names
    #        values - values to use for each variable
    #        address - URL address
    # Returns - a URL string with variables in the GET format
    url = address
    if values is not None:
      count = len(values)
    if names is None:
      names = []
      for n in range(count):
        names.append("var%d" % n)
    for n in range(count):
      if n == 0:
        url += "command?"
      else:
        url += "&"
      if values is None:
        url += "%s=%d" % (names[n], n)
      else:
        if isinstance(values[n], str):
          url += "%s=%s" % (names[n], values[n])
        elif isinstance(values[n], int):
          url += "%s=%d" % (names[n], values[n])
        elif isinstance(values[n], float):
          url += "%s=%f" % (names[n], values[n])
        elif values[n] is None:
          url += "%s=%s" % (names[n], None)
        elif isinstance(values[n], list):
          url += "%s=%s" % (names[n], values[n])
        else:
          UNKNOWN_TYPE
    return url

  def _createURLFromAjaxCommand(self, ajax_cmd, address=None):
    # Input: ajax_cmd - command dictionary from commandFactory
    # Output: URL
    names = ajax_cmd.keys()
    values = []
    for name in names:
      values.append(ajax_cmd[name])
    return self._createURL(values=values, names=names, address=address)

  def _URL2Request(self, url):
    # Input: url - URL string
    # Returns - request with count number of parameters
    return self.factory.get(url)

  def _verifyResponse(self, response, checkSessionid=True):
    self.assertEqual(response.status_code, 200)
    if checkSessionid:
      self.assertTrue(response.cookies.has_key('sessionid'))
    expected_keys = ['column_names', 'final_column_name', 
        'table_id', 'table_caption', 'data']
    self.assertTrue(response.context.keys().issuperset(expected_keys))

  ''' TESTS '''
     
  def testExtractDataFromRequest(self):
    url = self._createURL(values=[0, "one"])
    request = self._URL2Request(url)
    value = sv.extractDataFromRequest(request, "var0", convert=True)
    self.assertEqual(value, 0)
    value = sv.extractDataFromRequest(request, "var1")
    self.assertEqual(value, "one")

  def _testCreateCommandDict(self, cmd_names, values):
    url = self._createURL(names=cmd_names, values=values)
    request = self._URL2Request(url)
    result = sv.createCommandDict(request)
    test_values = list(values)
    if isinstance(test_values[4], int):
      test_values[4] -= 1  # Adjust for row index
    for n in range(len(DICT_NAMES)):
      if result[DICT_NAMES[n]] is not None:
        self.assertEqual(result[DICT_NAMES[n]], test_values[n])

  def testCreateCommandDict(self):
    values = ["Update", "Column", "dummy",      2,
              4,           9999]
    self._testCreateCommandDict(AJAX_NAMES, values)  # All values are present
    for n in range(len(AJAX_NAMES)):
      new_values = list(values)
      new_values[n] = ''
      self._testCreateCommandDict(AJAX_NAMES, new_values)
  
  def testSaveAndGetTable(self):
    request = self._URL2Request(self._createURL(count=1))  # a request
    self._addSessionToRequest(request)
    self.assertEqual(sv.getTable(request), None)
    table = Table("test")
    sv.saveTable(request, table)
    self.assertTrue(request.session.has_key(sv.TABLE_FILE_KEY))
    new_table = sv.getTable(request)
    self.assertEqual(new_table.getName(), table.getName())

  def test(self):
    # Test creation of the initial random table
    response = self._createBaseTable()
    self._verifyResponse(response)

  def testCommandReload(self):
    self._createBaseTable()
    # Do the refresh
    refresh_url = self._createBaseURL()
    response = self.client.get(refresh_url)
    self._verifyResponse(response, checkSessionid=False)

  def _testCommandCellUpdate(self, row_index, val):
    response = self._createBaseTable()
    table = self._getTableFromResponse(response)
    column_index = self._findColumnWithType(table, val)
    # Do the cell update
    create_table_url = self._createBaseURL()
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Cell'
    ajax_cmd['command'] = 'Update'
    ajax_cmd['row'] = table. _rowNameFromIndex(row_index)
    ajax_cmd['column'] = column_index
    ajax_cmd['value'] = val
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=create_table_url)
    response = self.client.get(command_url)
    table = self._getTableFromResponse(response)
    self.assertEqual(table.getCell(row_index, column_index), val)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("data"))
    self.assertEqual(content["data"], "OK")

  def _findColumnWithType(self, table, val):
    # Inputs: table - table being analyzed
    #         val - value whose type is to be matched
    # Returns the index of the column with the specified type or none
    result = None
    columns = table.getColumns()
    numpy_type = np.array([val]).dtype
    for index in range(1, table.numColumns()):
      col = columns[index]
      if numpy_type == col.getArrayType():
        result = index
      elif str(numpy_type)[0:2] == str(col.getArrayType())[0:2]:
        result = index
    return result

  def testCommandCellUpdate(self):
    ROW_INDEX = NROW - 1
    self._testCommandCellUpdate(ROW_INDEX, 9999)
    self._testCommandCellUpdate(ROW_INDEX, "aaa")
    self._testCommandCellUpdate(ROW_INDEX, "aaa bb")

  def _getTableFromResponse(self, response):
    table_filepath = response.client.session[sv.TABLE_FILE_KEY]
    return getTableFromFile(table_filepath)

  def _testCommandColumnDelete(self, base_url):
    # Tests for command delete with a given base_url to consider the
    # two use cases of the initial table and a reload
    # Input - base_url - base URL used in the request
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    # Do the column delete
    COLUMN_INDEX = 2
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Column'
    ajax_cmd['command'] = 'Delete'
    ajax_cmd['column'] = COLUMN_INDEX
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=base_url)
    response = self.client.get(command_url)
    # Check the table
    table = self._getTableFromResponse(response)
    columns = table.getColumns()
    self.assertEqual(len(columns), NCOL)  # Added the 'row' column
    self.assertEqual(columns[0].numCells(), NROW)

  def testCommandColumnDelete(self):
    self._testCommandColumnDelete(BASE_URL)

  def _testCommandColumnRename(self, base_url, new_name, is_successful_outcome):
    # Tests for command column rename with a given base_url to consider the
    # two use cases of the initial table and a reload
    # Input - base_url - base URL used in the request
    #         new_name - new column name
    #         is_successful_outcome - Boolean whether rename is successful
    base_response = self._createBaseTable()
    # Do the cell update
    COLUMN_INDEX = 2
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Column'
    ajax_cmd['command'] = 'Rename'
    ajax_cmd['column'] = COLUMN_INDEX
    ajax_cmd['args[]'] = new_name.replace(' ', '+')
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=base_url)
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
      self.assertEqual(columns[0].numCells(), NROW)
      self.assertEqual(columns[COLUMN_INDEX].getName(), new_name)

  def testCommandColumnRename(self):
    new_name = 'row'  # duplicate name
    self._testCommandColumnRename(BASE_URL, new_name, False)
    NEW_NAME = "New_Column"
    self._testCommandColumnRename(BASE_URL, NEW_NAME, True)

  def testCommandRowMove(self):
    # Tests row renaming by moving the first row
    # to the end of the table
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    num_rows = len(table_data[0])
    num_columns = table.numColumns()
    rplIdx = range(num_rows)
    del rplIdx[0]
    rplIdx.append(0)
    new_row_name = table._rowNameFromIndex(table.numRows())
    # Do the cell update
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = 'Move'
    ajax_cmd['row'] = 1
    ajax_cmd['args[]'] = new_row_name
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numRows(), num_rows)
    self.assertEqual(new_table.numColumns(), num_columns)
    new_table_data = new_table.getData()
    for c in range(1, num_columns):
      expected_array = np.array([table_data[c][n] for n in rplIdx])
      b = (new_table_data[c] == expected_array).all()
      self.assertTrue(b)

  def testCommandRowDelete(self):
    ROW_IDX = 1
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    num_rows = len(table_data[0])
    num_columns = table.numColumns()
    rplIdx = range(num_rows)
    del rplIdx[ROW_IDX - 1]
    # Do the cell update
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = 'Delete'
    ajax_cmd['row'] = ROW_IDX
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numRows(), num_rows - 1)
    self.assertEqual(new_table.numColumns(), num_columns)
    new_table_data = new_table.getData()
    for c in range(1, num_columns):
      expected_array = np.array([table_data[c][n] for n in rplIdx])
      b = (new_table_data[c] == expected_array).all()
      self.assertTrue(b)

  def _addRow(self, command, cur_idx, new_idx):
    # Inputs: command - string of command to issue
    #         cur_idx - index of the current row
    #         new_idx - index of the new row
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    num_rows = table.numRows()
    num_columns = table.numColumns()
    row_name = table._rowNameFromIndex(cur_idx)
    # Do the cell update
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = command
    ajax_cmd['row'] = row_name
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
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
    self._addRow("Insert", 0, 0)
    self._addRow("Insert", NROW - 1, NROW - 1)
    self._addRow("Insert", 2, 2)

  def testCommandRowAppend(self):
    self._addRow("Append", 0, 1)
    self._addRow("Append", NROW - 1, NROW)
    self._addRow("Append", 2, 3)

  def _addColumn(self, command, cur_idx, new_idx):
    # Inputs: command - string of command to issue
    #         cur_idx - index of the current column
    #         new_idx - index of the new column
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    num_rows = table.numRows()
    num_columns = table.numColumns()
    # Do the cell update
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Column'
    ajax_cmd['command'] = command
    ajax_cmd['column'] = cur_idx
    ajax_cmd['args[]'] = 'Yet_Another_Column'
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
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
    self._addColumn("Insert", 1, 1)
    self._addColumn("Insert", 2, 2)
    self._addColumn("Insert", NCOL, NCOL)

  def testCommandColumnAppend(self):
    self._addColumn("Append", 1, 2)
    self._addColumn("Append", 2, 3)
    self._addColumn("Append", NCOL, NCOL+1)

  def _moveColumn(self, column_idx_to_move, dest_column_name):
    # Inputs: column_idx_to_move - index of column to be moved
    #         dest_column_name - name of the dest column after
    #         which the column is to be moved
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    num_rows = table.numRows()
    num_columns = table.numColumns()
    moved_column = table.columnFromIndex(column_idx_to_move)
    dest_column = table.columnFromName(dest_column_name)
    expected_index = table.indexFromColumn(dest_column)
    # Do the cell update
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Move"
    ajax_cmd['column'] = column_idx_to_move
    ajax_cmd['args[]'] = dest_column_name
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numColumns(), num_columns)
    self.assertEqual(new_table.numRows(), num_rows)
    # New column should have all None values
    column = new_table.getColumns()[expected_index]
    self.assertEqual(column.getName(), moved_column.getName())
    b = all([column.getCells()[n] == moved_column.getCells()[n] 
             for n in range(column.numCells())])
    if not b:
      import pdb; pdb.set_trace()
    self.assertTrue(b)
  
  def _makeColumnName(self, column_index):
    return "Col_%d" % column_index

  def testCommandColumnMove(self):
    # The column names are "row", "Col_0", ...
    self._moveColumn(1, self._makeColumnName(NCOL-1))  # Make it the last column

  def _formulaColumn(self, column_idx, formula, isValid):
    # Inputs: column_idx - index of column whose formula is changed
    #         formula - new formula for column
    #         isValid - is a valid formula
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    column = table.columnFromIndex(column_idx)
    old_formula = column.getFormula()
    # Reset the formula
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['column'] = column_idx
    ajax_cmd['args[]'] = formula
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    # Check the table
    new_table = self._getTableFromResponse(response)
    new_column = new_table.columnFromIndex(column_idx)
    if isValid:
      self.assertTrue(content["success"])
      self.assertEqual(formula, new_column.getFormula())
    else:
      self.assertFalse(content["success"])
      self.assertEqual(old_formula, new_column.getFormula())

  def testCommandColumnFormula(self):
    self._formulaColumn(NCOL - 1, "np.sin(2.3)", True)  # Valid formula
    self._formulaColumn(NCOL - 1, "np.sin(2.3", False)  # Invalid formula

  def _evaluateTable(self, formula, isValid, col_idx=NCOL-1):
    # Inputs: formula - new formula for column
    #         isValid - is a valid formula
    base_response = self._createBaseTable()
    # Change the formula
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['column'] = col_idx
    ajax_cmd['args[]'] = formula
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    # Check the table
    new_table = self._getTableFromResponse(response)
    error = new_table.evaluate()
    if isValid:
      self.assertTrue(content["success"])
    else:
      self.assertFalse(content["success"])

  def testTableEvaluate(self):
    self._evaluateTable("np.sin(3.2)", True)  # Valid formula
    self._evaluateTable("range(1000)", True)  # Test large
    formula = "Col_2 = np.sin(np.array(range(10), dtype=float));B =  Col_1**3"
    self._evaluateTable(formula, True)  # Compound formula
    self._evaluateTable("np.sin(x)", False)  # Invalid formula

  def testTableExport(self):
    # Populate the table with a couple of formulas
    FORMULA = "range(10)"
    FUNC_NAME = "ss_export_test"
    self._evaluateTable(FORMULA, True)
    # Do the export
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = "Table"
    ajax_cmd['command'] = "Export"
    inputs = "Col_1"
    outputs = "Col_%d, Col_%d" % (NCOL-1, NCOL-2)
    arg_list = [FUNC_NAME, inputs, outputs]
    ajax_cmd['args[]'] = arg_list
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))

  def _tableTrim(self, row_idx, expected_number_rows):
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    table_data = table.getData()
    row_name = table._rowNameFromIndex(row_idx)
    # Add the row
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Row'
    ajax_cmd['command'] = 'Append'
    ajax_cmd['row'] = row_name
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Do the trim
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'Trim'
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numRows(), expected_number_rows)

  def testTableTrim(self):
    self._tableTrim(0, NROW+1)
    self._tableTrim(NROW, NROW)

  def _tableRename(self, new_name, is_valid_name):
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    old_name = table.getName()
    # Rename the table
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'Rename'
    ajax_cmd['args[]'] = new_name
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
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
      self.assertEqual(new_table.getName(), new_name)
    else:
      self.assertFalse(content["success"])
      self.assertEqual(new_table.getName(), old_name)

  def testTableRename(self):
    self._tableRename("valid_name", True)
    self._tableRename("invalid_name!", False)

  def testTableListTableFiles(self):
    filename = "dummy"
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    helper.create()
    base_response = self._createBaseTable()
    table = self._getTableFromResponse(base_response)
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'ListTableFiles'
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])
    self.assertTrue("data" in content)
    self.assertTrue(filename in content["data"])
    helper.destroy()

  def testTableOpenTableFiles(self):
    filename = "dummy"
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    helper.create()
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'OpenTableFile'
    ajax_cmd['args[]'] = filename
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
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
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'SaveAs'
    ajax_cmd['args[]'] = filename
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])

  def testTableSave(self):
    filename = "dummy"
    _ = self._createBaseTable()
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    helper.create()
    self._tableSave(filename)
    helper.destroy()

  def testTableDelete(self):
    filename = "dummy"
    helper = TableFileHelper(filename, st.SCISHEETS_USER_TBLDIR)
    _ = self._createBaseTable()
    helper.create()
    self._tableSave(filename)
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'Delete'
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])
    self.assertFalse(TableFileHelper.doesTableFileExist(filename,
        st.SCISHEETS_USER_TBLDIR))
    #helper.destroy()

  def testTableNew(self):
    filename = sv.LOCAL_FILE
    _ = self._createBaseTable()
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = 'Table'
    ajax_cmd['command'] = 'New'
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue("success" in content)
    self.assertTrue(content["success"])
    self.assertTrue(TableFileHelper.doesTableFileExist(filename,
        st.SCISHEETS_USER_TBLDIR))

  def testFormulaRowAddition(self):
    base_response = self._createBaseTable()
    # Change the formula
    ajax_cmd = self._ajaxCommandFactory()
    ajax_cmd['target'] = "Column"
    ajax_cmd['command'] = "Formula"
    ajax_cmd['column'] = 1
    num_rows = 2*NROW
    ajax_cmd['args[]'] = "range(%d)" % num_rows
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    content = json.loads(response.content)
    self.assertTrue(content.has_key("success"))
    # Check the table
    table = self._getTableFromResponse(response)
    error = table.evaluate()
    self.assertTrue(content["success"])
    self.assertEqual(table.numRows(), num_rows)


if __name__ == '__main__':
    unittest.main()

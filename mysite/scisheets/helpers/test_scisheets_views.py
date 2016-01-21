'''Tests for scisheets_views'''

from mysite import settings
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from ..core.table import Table
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
  
  def testPickle_unPickle(self):
    request = self._URL2Request(self._createURL(count=1))  # a request
    self._addSessionToRequest(request)
    self.assertEqual(sv.unPickleTable(request), None)
    table = Table("test")
    sv.pickleTable(request, table)
    self.assertTrue(request.session.has_key(sv.PICKLE_KEY))
    new_table = sv.unPickleTable(request)
    self.assertEqual(new_table.getName(), table.getName())

  def testScisheets(self):
    # Test creation of the initial random table
    response = self._createBaseTable()
    self._verifyResponse(response)

  def testScisheetsCommandReload(self):
    self._createBaseTable()
    # Do the refresh
    refresh_url = self._createBaseURL()
    response = self.client.get(refresh_url)
    self._verifyResponse(response, checkSessionid=False)

  def _testScisheetsCommandCellUpdate(self, row_index, val):
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
    for index in range(1, table.numColumns()):
      col = columns[index]
      if isinstance(val, col.getDataType()) and (result is None):
        if isinstance(val, float) and (col.getDataType() == float):
          result = index
        if isinstance(val, int) and (col.getDataType() == int):
          result = index
        if not isinstance(val, int):
          result = index
    return result

  def testScisheetsCommandCellUpdate(self):
    ROW_INDEX = NROW - 1
    self._testScisheetsCommandCellUpdate(ROW_INDEX, 9999)
    self._testScisheetsCommandCellUpdate(ROW_INDEX, "aaa")
    self._testScisheetsCommandCellUpdate(ROW_INDEX, "aaa bb")

  def _getTableFromResponse(self, response):
    pickle_file = response.client.session[sv.PICKLE_KEY]
    return sv._getTable(pickle_file)

  def _testScisheetsCommandColumnDelete(self, base_url):
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

  def testScisheetsCommandColumnDelete(self):
    self._testScisheetsCommandColumnDelete(BASE_URL)

  def _testScisheetsCommandColumnRename(self, base_url, new_name, is_successful_outcome):
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

  def testScisheetsCommandColumnRename(self):
    new_name = 'row'  # duplicate name
    self._testScisheetsCommandColumnRename(BASE_URL, new_name, False)
    NEW_NAME = "New Column"
    self._testScisheetsCommandColumnRename(BASE_URL, NEW_NAME, True)

  def testScisheetsCommandRowMove(self):
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
      expected_array = table_data[c][rplIdx]
      b = (new_table_data[c] == expected_array).all()
      self.assertTrue(b)

  def testScisheetsCommandRowDelete(self):
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
      expected_array = table_data[c][rplIdx]
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
    # New row should have all none values
    new_row = new_table.getRow(new_idx)
    values = []
    for k in new_row.keys():
      if k != 'row':
        values.append(new_row[k])
    b = np.equal(np.array(values), None).all()
    self.assertTrue(b)  # New row should be 'None'

  def testScisheetsCommandRowInsert(self):
    self._addRow("Insert", 0, 0)
    self._addRow("Insert", NROW - 1, NROW - 1)
    self._addRow("Insert", 2, 2)

  def testScisheetsCommandRowAppend(self):
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
    command_url = self._createURLFromAjaxCommand(ajax_cmd, address=BASE_URL)
    response = self.client.get(command_url)
    # Check the table
    new_table = self._getTableFromResponse(response)
    self.assertEqual(new_table.numColumns(), num_columns + 1)
    self.assertEqual(new_table.numRows(), num_rows)
    # New column should have all None values
    new_column = new_table.getColumns()[new_idx]
    self.assertTrue(new_column.numCells(), num_rows)
    b = np.equal(new_column.getCells(), None).all()
    if not b:
      import pdb; pdb.set_trace()
    self.assertTrue(b)

  def testScisheetsCommandColumnInsert(self):
    self._addColumn("Insert", 1, 1)
    self._addColumn("Insert", 2, 2)
    self._addColumn("Insert", NCOL, NCOL)

  def testScisheetsCommandColumnAppend(self):
    self._addColumn("Append", 1, 2)
    self._addColumn("Append", 2, 3)
    self._addColumn("Append", NCOL, NCOL+1)

  def _moveColumn(self, column_idx_to_move, dest_column_name):
    # Inputs: command - string of command to issue
    #         cur_idx - index of the current column
    #         new_idx - index of the new column
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
    b = np.equal(column.getCells(), moved_column.getCells()).all()
    if not b:
      import pdb; pdb.set_trace()
    self.assertTrue(b)
  
  def _makeColumnName(self, column_index):
    return "Col-%d" % column_index

  def testScisheetsCommandColumnMove(self):
    # The column names are "row", "Col-0", ...
    self._moveColumn(1, self._makeColumnName(NCOL-1))  # Make it the last column


if __name__ == '__main__':
    unittest.main()

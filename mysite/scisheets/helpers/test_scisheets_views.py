'''Tests for scisheets_views'''

from mysite import settings
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from ..core.table import Table
import mysite.helpers.util as ut
import scisheets_views as sv
import os


NCOL = 3
NROW = 4
BASE_URL = "http://localhost:8000/scisheets/"
TABLE_PARAMS = [NCOL, NROW]


class TestScisheetsViews(TestCase):
 
  def setUp(self):
    self.factory = RequestFactory()

  def _addSessionToRequest(self, request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

  def _commandDictFactory(self):
    TARGET = 'Cell'
    COMMAND = 'Update'
    VALUE = 'XXX'
    ROW_INDEX = 1
    COLUMN_INDEX = 3
    TABLE_NAME = 'XYZ'
    cmd_dict = {}
    cmd_dict['target'] = TARGET
    cmd_dict['command'] = COMMAND
    cmd_dict['value'] = VALUE
    cmd_dict['row_index'] = ROW_INDEX
    cmd_dict['column_index'] = COLUMN_INDEX
    cmd_dict['table_name'] = TABLE_NAME
    return cmd_dict

  def _createURL(self, address="dummy", count=None, values=None, names=None):
    # Input: count - number of variables
    #        names - variable names
    #        values - values to use for each variable
    #        address - URL address
    # Returns - a URL string
    url = address
    if values is not None:
      count = len(values)
    if names is None:
      names = []
      for n in range(count):
        names.append("var%d" % n)
    for n in range(count):
      if n == 0:
        url += "?"
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
        else:
          url += "%s=%s" % (names[n], None)
    return url

  def _URL2Request(self, url):
    # Input: url - URL string
    # Returns - request with count number of parameters
    return self.factory.get(url)

  def _createURLFromCommandDict(self, cmd_dict, address=None):
    # Input: cmd_dict - command dictionary from commandFactory
    # Output: URL
    names = cmd_dict.keys()
    values = []
    for k in names:
      values.append(cmd_dict[k])
    return self._createURL(values=values, names=names, address=address)

  def testCreateCommandDict(rquest):
    cmd_dict = sv.createCommandDict(self.request)
    self.assertEqual(len(cmd_dict.keys()), len(self.cmd.keys()))
    for k in self.cmd.keys():
     self.assertEqual(cmd_dict[k], self.cmd[k])
     
  def testExtractDataFromRequest(self):
    request = self._URL2Request(self._createURL(values=[0, "one"]))
    value = sv.extractDataFromRequest(request, "var0")
    self.assertEqual(value, 0)
    value = sv.extractDataFromRequest(request, "var1")
    self.assertEqual(value, "one")

  def testCreateCommandDict(self):
    request_names = ["command", "target", "table", "column",
                     "row", "value"]
    values = ["update", "column", "dummy",      2,
              4,           9999]
    dict_names = ["command", "target", "table_name", "column_index",
                     "row_index", "value"]
    test_values = list(values)
    test_values[4] -= 1  # Adjust for row index
    request = self._URL2Request(self._createURL(names=request_names, values=values))
    result = sv.createCommandDict(request)
    for n in range(len(dict_names)):
      self.assertEqual(result[dict_names[n]], test_values[n])
  
  def testPickle_unPickle(self):
    request = self._URL2Request(self._createURL(count=1))  # a request
    self._addSessionToRequest(request)
    self.assertEqual(sv.unPickleTable(request), None)
    table = Table("test")
    sv.pickleTable(request, table)
    self.assertTrue(request.session.has_key(sv.PICKLE_KEY))
    new_table = sv.unPickleTable(request)
    self.assertEqual(new_table.getName(), table.getName())

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

  def _createBaseTable(self):
    # Create the table
    create_table_url = self._createBaseURL(params=TABLE_PARAMS)
    return self.client.get(create_table_url)

  def _verifyResponse(self, response, checkSessionid=True):
    self.assertEqual(response.status_code, 200)
    if checkSessionid:
      self.assertTrue(response.cookies.has_key('sessionid'))
    expected_keys = ['column_names', 'final_column_name', 
        'table_id', 'table_caption', 'data']
    self.assertTrue(response.context.keys().issuperset(expected_keys))

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

  def testScisheetsCommandCellUpdate(self):
    self._createBaseTable()
    # Do the cell update
    create_table_url = self._createBaseURL(params=TABLE_PARAMS)
    ROW_INDEX =1
    COLUMN_INDEX = 2
    VALUE = 9999
    cmd_dict = self._commandDictFactory()
    cmd_dict['target'] = 'Cell'
    cmd_dict['command'] = 'Update'
    cmd_dict['row_index'] = ROW_INDEX
    cmd_dict['column_index'] = COLUMN_INDEX
    cmd_dict['value'] = VALUE
    command_url = self._createURLFromCommandDict(cmd_dict, address=create_table_url)
    response = self.client.get(command_url)
    self._verifyResponse(response, checkSessionid=False)

  def testScisheetsCommandColumnDelete(self):
    self._createBaseTable()
    # Do the cell update
    create_table_url = self._createBaseURL(params=TABLE_PARAMS)
    COLUMN_INDEX = 2
    cmd_dict = self._commandDictFactory()
    cmd_dict['target'] = 'Column'
    cmd_dict['command'] = 'Delete'
    cmd_dict['column_index'] = COLUMN_INDEX
    command_url = self._createURLFromCommandDict(cmd_dict, address=create_table_url)
    response = self.client.get(command_url)
    self._verifyResponse(response, checkSessionid=False)


if __name__ == '__main__':
    unittest.main()

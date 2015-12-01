'''Tests for scisheets_views'''

from mysite import settings
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from ..core.table import Table
import mysite.helpers.util as ut
import scisheets_views as sv
import os


class TestScisheetsViews(TestCase):
 
  def setUp(self):
    self.factory = RequestFactory()

  def _createRequestWithCommand(self):
    TARGET = 'Cell'
    COMMAND = 'Update'
    VALUE = 'XXX'
    ROW_INDEX = 1
    COLUMN_INDEX = 3
    TABLE_NAME = 'XYZ'
    cmd_dict = self._commandFactory()
    cmd_dict['target'] = TARGET
    cmd_dict['command'] = COMMAND
    cmd_dict['value'] = VALUE
    cmd_dict['row_index'] = ROW_INDEX
    cmd_dict['column_index'] = COLUMN_INDEX
    cmd_dict['table_name'] = TABLE_NAME
    request = self._createRequestFromCommandDict(cmd_dict)
    return request

  def _addSessionToRequest(self, request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

  def _commandFactory(self):
    cmd_dict = {}
    cmd_dict['command'] = None
    cmd_dict['target'] = None
    cmd_dict['table_name'] = None
    cmd_dict['column_index'] = None
    cmd_dict['row_index'] = None
    cmd_dict['value'] = None
    return cmd_dict

  def _createURL(self, address="dummy", count=None, values=None, names=None):
    # Input: count - number of variables
    #        names - variable names
    #        values - values to use for each variable
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

  def _createRequestFromCommandDict(self, cmd_dict):
    # Input: cmd_dict - command dictionary from commandFactory
    # Output: HTML request with session variable
    names = cmd_dict.keys()
    values = []
    for k in names:
      values.append(cmd_dict[k])
    request = self._URL2Request(self._createURL(values=values, names=names))
    self._addSessionToRequest(request)

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

  def testScisheets(self):
    NCOL = 3
    NROW = 4
    client_url = "http://localhost:8000/scisheets/%d/%d/" % (NCOL, NROW)
    response = self.client.get(client_url)
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.cookies.has_key('sessionid'))
    expected_keys = ['column_names', 'final_column_name', 
        'table_id', 'table_caption', 'data']
    self.assertTrue(response.context.keys().issuperset(expected_keys))


if __name__ == '__main__':
    unittest.main()

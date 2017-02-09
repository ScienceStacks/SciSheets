'''Tests for CommandDict.'''

from command_dict import CommandDict, _extractDataFromRequest
import scisheets.core.helpers.cell_types as cell_types
from django.test import TestCase, RequestFactory

NCOL = 3
NROW = 4
BASE_URL = "http://localhost:8000/scisheets/"
IGNORE_TEST = False
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
    ajax_cmd = {}
    ajax_cmd['target'] = TARGET
    ajax_cmd['command'] = COMMAND
    ajax_cmd['value'] = VALUE
    ajax_cmd['row'] = ROW_INDEX
    ajax_cmd['columnName'] = COLUMN_NAME
    ajax_cmd['table'] = TABLE_NAME
    ajax_cmd['args[]'] = None
    return ajax_cmd

  def _createBaseTable(self, params=TABLE_PARAMS):
    # Create the table
    # Output - response from command
    create_table_url = self._createBaseURL(params=params)
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
    count = 0
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
        if cell_types.isStr(values[n]):
          url += "%s=%s" % (names[n], values[n])
        elif isinstance(values[n], int):
          url += "%s=%d" % (names[n], values[n])
        elif cell_types.isFloats([n]):
          url += "%s=%f" % (names[n], values[n])
        elif values[n] is None:
          url += "%s=%s" % (names[n], None)
        elif isinstance(values[n], list):
          url += "%s=%s" % (names[n], values[n])
        else:
          import pdb; pdb.set_trace()
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
    expected_keys = ['column_hierarchy', 'response_schema', 
        'table_id', 'table_caption', 'data']
    sef.assertTrue(response.context.keys().issuperset(expected_keys))

  def testExtractDataFromRequest(self):
    if IGNORE_TEST:
       return
    url = self._createURL(values=[0, "one"])
    request = self._URL2Request(url)
    value = _extractDataFromRequest(request, "var0", convert=True)
    self.assertEqual(value, 0)
    value = _extractDataFromRequest(request, "var1")
    self.assertEqual(value, "one")

  def testCreateCommandDict(self):
    a_dict = {'a': 1, 'b': 2}
    cmd_dict = CommandDict.createCommandDict(a_dict)
    self.assertEqual(cmd_dict['a'], a_dict['a'])
    self.assertEqual(cmd_dict['b'], a_dict['b'])


if __name__ == '__main__':
    unittest.main()

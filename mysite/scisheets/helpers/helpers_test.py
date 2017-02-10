'''Client Mocks'''

import scisheets.core.helpers.cell_types as cell_types
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

BASE_URL = "http://localhost:8000/scisheets/"
TARGET = 'Cell'
COMMAND = 'Update'
VALUE = 'XXX'
ROW_INDEX = 1
COLUMN_INDEX = 3
COLUMN_NAME = 'Col_2'
TABLE_NAME = 'XYZ'
IGNORE_TEST = False


class HelperHTTP(object):
 
  def __init__(self):
    self._factory = RequestFactory()

  def addSessionToRequest(self, request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

  def ajaxCommandFactory(self):
    ajax_cmd = {}
    ajax_cmd['target'] = TARGET
    ajax_cmd['command'] = COMMAND
    ajax_cmd['value'] = VALUE
    ajax_cmd['row'] = ROW_INDEX
    ajax_cmd['columnName'] = COLUMN_NAME
    ajax_cmd['table'] = TABLE_NAME
    ajax_cmd['args[]'] = None
    return ajax_cmd

  def createBaseURL(self, params=None):
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

  def createURL(self, address="dummy", count=None, values=None, names=None):
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

  def createURLFromAjaxCommand(self, ajax_cmd, address=None):
    # Input: ajax_cmd - command dictionary from commandFactory
    # Output: URL
    names = ajax_cmd.keys()
    values = []
    for name in names:
      values.append(ajax_cmd[name])
    return self.createURL(values=values, names=names, address=address)

  def URL2Request(self, url):
    # Input: url - URL string
    # Returns - request with count number of parameters
    return self._factory.get(url)

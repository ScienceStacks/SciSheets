'''Tests for CommandDict.'''

from scisheets.helpers.command_dict import CommandDict, _extractDataFromRequest
import scisheets.core.helpers.cell_types as cell_types
from django.test import TestCase, RequestFactory
from scisheets.helpers.helpers_test import HelperHTTP

NCOL = 3
NROW = 4
BASE_URL = "http://localhost:8000/scisheets/"
IGNORE_TEST = False
TABLE_PARAMS = [NCOL, NROW]


class TestScisheetsViews(TestCase):
 
  def setUp(self):
    self._helper_http = HelperHTTP()

  def testExtractDataFromRequest(self):
    if IGNORE_TEST:
       return
    url = self._helper_http.createURL(values=[0, "one"])
    request = self._helper_http.URL2Request(url)
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

'''Tests for UITable.'''

from mysite import settings
import dj_table as dj
from django.test import TestCase  # Provides mocks
import json


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
NCOL = 4
NROW = 3
TABLE_NAME = "MY TABLE"


class TestAuxFunctions(TestCase):

  def _testMakeJSONStr(self, column_names, column_data, data_type):
    json_str = dj.makeJSON(column_names, column_data)
    converted = json.loads(json_str.replace("`", '"'))
    self.assertTrue(isinstance(converted, list))
    self.assertEqual(len(converted[0]), len(column_names))
    for n in range(len(converted)):
      self.assertTrue(isinstance(converted[n], dict))

  def testMakeJSONStr(self):
    self._testMakeJSONStr(COLUMN_NAMES, DATA, list)
    self._testMakeJSONStr(COLUMN_NAMES, DATA_STRING, str)


class TestUITable(TestCase):

  def setUp(self):
    self.table = dj.DJTable.createRandomTable(TABLE_NAME,
        NROW, NCOL)

  # TODO: Do something better with this test
  def testRender(self):
    Col_0 = self.table.getColumns()[1]
    Col_0.setFormula("Col_1 = 'x'")
    self.table.evaluate()
    html = self.table.render()
    self.assertIsNotNone(html)

if __name__ == '__main__':
    unittest.man()

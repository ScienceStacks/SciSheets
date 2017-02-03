'''Tests for UITable for Sheet commands.'''

from mysite import settings
from scisheets.core.helpers.serialize_deserialize import serialize,  \
    deserialize
from scisheets.core.column import Column
from scisheets.core.table import NAME_COLUMN_STR
import ui_table as ui
from django.test import TestCase  # Provides mocks
import json


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
NCOL = 30
NROW = 3
TABLE_NAME = "MY_TABLE"
IGNORE_TEST = True
    

class TestUITableUtility(TestCase):

  def testAddEscapesToQuotes(self):
    if IGNORE_TEST:
      return
    list_of_str = ["xy", "x'y'"]
    mod_list_of_str = ui.UITable._addEscapesToQuotes(list_of_str)
    self.assertEqual(mod_list_of_str[1].index("\\"), 1)
    list_of_str = range(3)
    mod_list_of_str = ui.UITable._addEscapesToQuotes(list_of_str)
    self.assertTrue(list_of_str == mod_list_of_str)

  def testSerializeDeserialize(self):
    if IGNORE_TEST:
      return
    json_str = serialize(self.table)
    new_table = deserialize(json_str)
    self.assertTrue(self.table.isEquivalent(new_table))


class TestUITableSheet(TestCase):

  def setUp(self):
    self.table = ui.UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, 3*NCOL, 0.3, prob_detach=0.2)
    

if __name__ == '__main__':
    unittest.man()

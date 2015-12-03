'''Tests for UITable.'''

from mysite import settings
import ui_table as ui
from django.test import TestCase  # Provides mocks
import json


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
NCOL = 4
NROW = 3
TABLE_NAME = "MY TABLE"


class TestAuxFunctions(TestCase):

  def testMakeJSONStr(self):
    json_str = ui.makeJSONStr(COLUMN_NAMES, DATA)
    converted = json.loads(json_str[1:-1])
    self.assertTrue(isinstance(converted, list))
    self.assertEqual(len(converted), len(COLUMN_NAMES))
    for n in range(len(COLUMN_NAMES)):
      self.assertTrue(isinstance(converted[n], dict))
    

class TestUITable(TestCase):

  def setUp(self):
    self.table = ui.UITable.createRandomIntTable(TABLE_NAME,
        NROW, NCOL)

  def testCreateRandomIntTable(self):
    self.assertEqual(self.table.numRows(), NROW)
    self.assertEqual(self.table.numColumns(), NCOL+1)  # Include name col
    NCOLSTR = 2
    new_table = ui.UITable.createRandomIntTable(TABLE_NAME,
        NROW, NCOL, ncolstr=NCOLSTR)
    num_str_col = 0
    for n in range(1, NCOL):
      cell = new_table.getColumns()[n].getCells()[0]
      if isinstance(cell, str):
        num_str_col += 1
    self.assertEqual(num_str_col, NCOLSTR)

  def testProcessCommandCellUpdate(self):
    COLUMN_INDEX = 3
    ROW_INDEX = 2
    NEW_VALUE = 9999
    cmd_dict = {
                'target':  'Cell',
                'command': 'Update',
                'table_name': None,
                'column_index': COLUMN_INDEX,
                'row_index': ROW_INDEX,
                'value': NEW_VALUE
               }
    self.table.processCommand(cmd_dict)
    self.assertEqual(int(self.table.getCell(ROW_INDEX, COLUMN_INDEX)),
      NEW_VALUE)

  def testProcessCommandColumnDelete(self):
    COLUMN_INDEX = 3
    ROW_INDEX = None
    NEW_VALUE = None
    old_num_columns = self.table.numColumns()
    aRow = self.table.getRow(0)
    deleted_column_name = self.table.getColumns()[COLUMN_INDEX].getName()
    cmd_dict = {
                'target':  'Column',
                'command': 'Delete',
                'table_name': None,
                'column_index': COLUMN_INDEX,
                'row_index': ROW_INDEX,
                'value': NEW_VALUE
               }
    self.table.processCommand(cmd_dict)
    expected_num_columns = old_num_columns - 1
    self.assertEqual(self.table.numColumns(), expected_num_columns)
    bRow = self.table.getRow(0)
    for k in bRow.keys():
      self.assertEqual(bRow[k], aRow[k])

  # TODO: Do something better with this test
  def testRender(self):
    html = self.table.render()
    self.assertIsNotNone(html)
    


if __name__ == '__main__':
    unittest.man()

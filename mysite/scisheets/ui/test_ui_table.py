'''Tests for UITable.'''

from mysite import settings
import ui_table as ui
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
    json_str = ui.makeJSONStr(column_names, column_data)
    converted = json.loads(json_str[1:-1])
    self.assertTrue(isinstance(converted, list))
    self.assertEqual(len(converted[0]), len(column_names))
    for n in range(len(converted)):
      self.assertTrue(isinstance(converted[n], dict))

  def testMakeJSONStr(self):
    self._testMakeJSONStr(COLUMN_NAMES, DATA, list)
    self._testMakeJSONStr(COLUMN_NAMES, DATA_STRING, str)
    

class TestUITable(TestCase):

  def setUp(self):
    self.table = ui.UITable.createRandomTable(TABLE_NAME,
        NROW, NCOL)

  def testCreateRandomTable(self):
    self.assertEqual(self.table.numRows(), NROW)
    self.assertEqual(self.table.numColumns(), NCOL+1)  # Include name col
    NCOLSTR = min(2, NCOL)
    new_table = ui.UITable.createRandomTable(TABLE_NAME,
        NROW, NCOL, ncolstr=NCOLSTR)
    num_str_col = 0
    for n in range(1, NCOL+1):  # Added the name column
      cell = new_table.getColumns()[n].getCells()[0]
      if isinstance(cell, str):
        num_str_col += 1
    self.assertEqual(num_str_col, NCOLSTR)
    self.assertEqual(new_table.numColumns(), NCOL + 1)  # Include the 'row' column
    self.assertEqual(new_table.numRows(), NROW)

  def testProcessCommandCellUpdate(self):
    before_table = self.table.copy()
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
    for c in range(self.table.numColumns()):
      self.assertEqual(before_table.getColumns()[c].getName(), 
          self.table.getColumns()[c].getName())
      for r in range(self.table.numRows()):
        if not (r == ROW_INDEX and c == COLUMN_INDEX):
          self.assertEqual(before_table.getCell(r,c), 
              self.table.getCell(r,c))

  def testProcessCommandColumnDelete(self):
    COLUMN_INDEX = 3
    ROW_INDEX = None
    NEW_VALUE = None
    old_num_columns = self.table.numColumns()
    before_table = self.table.copy()
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
    for r in range(self.table.numRows()):
      after_row = self.table.getRow(r)
      before_row = before_table.getRow(r)
      for k in after_row.keys():
        self.assertEqual(after_row[k], before_row[k])

  def testProcessCommandColumnRename(self):
    COLUMN_INDEX = 3
    ROW_INDEX = None
    NEW_VALUE = None
    NEW_COLUMN_NAME = "New Name"
    cmd_dict = {
                'target':  'Column',
                'command': 'Rename',
                'table_name': None,
                'column_index': COLUMN_INDEX,
                'row_index': ROW_INDEX,
                'args': [NEW_COLUMN_NAME],
                'value': NEW_VALUE,
               }
    old_num_columns = self.table.numColumns()
    self.table.processCommand(cmd_dict)
    self.assertEqual(self.table.numColumns(), old_num_columns)
    self.assertEqual(self.table.getColumns()[COLUMN_INDEX].getName(), NEW_COLUMN_NAME)

  # TODO: Do something better with this test
  def testRender(self):
    html = self.table.render()
    self.assertIsNotNone(html)
    


if __name__ == '__main__':
    unittest.man()

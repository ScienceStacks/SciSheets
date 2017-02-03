'''Tests for UITable Cell commands.'''

from mysite import settings
from scisheets.core.column import Column
import ui_table as ui
from django.test import TestCase  # Provides mocks


# Constants
NCOL = 30
NROW = 3
TABLE_NAME = "MY_TABLE"
IGNORE_TEST = True
    

class TestUITableCell(TestCase):

  def setUp(self):
    self.table = ui.UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, 3*NCOL, 0.3, prob_detach=0.2)

  def testProcessCommandCellUpdate(self):
    if IGNORE_TEST:
      return
    table = ui.UITable.createRandomTable(TABLE_NAME,
        NROW, NCOL)
    before_table = table.copy()
    column_index = 3
    column = table.getChildAtPosition(column_index)
    column_name = column.getName(is_global_name=False)
    ROW_INDEX = 2
    NEW_VALUE = 9999
    cmd_dict = {
                'target':  'Cell',
                'command': 'Update',
                'table_name': None,
                'column_name': column_name,
                'row_index': ROW_INDEX,
                'value': NEW_VALUE
               }
    table.processCommand(cmd_dict)
    self.assertEqual(int(table.getCell(ROW_INDEX, column_name)),
      NEW_VALUE)
    for c in range(table.numColumns()):
      self.assertEqual(before_table.getColumns()[c].getName(), 
          table.getColumns()[c].getName())
      for r in range(table.numRows()):
        if not (r == ROW_INDEX and c == column_index):
          self.assertEqual(before_table.getCell(r,c), 
              table.getCell(r,c))
    

if __name__ == '__main__':
    unittest.man()

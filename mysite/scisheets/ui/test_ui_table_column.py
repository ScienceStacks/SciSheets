'''Tests for UITable for Column Commands.'''

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
    

class TestUITableCell(TestCase):

  def setUp(self):
    self.table = ui.UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, 3*NCOL, 0.3, prob_detach=0.2)

  def _testProcessCommandColumnDelete(self, target):
    """
    :param str target: Table or Column
    """
    if target == "Table":
      non_leaves  = self.table.getNonLeaves()
      column = non_leaves[-1]
    else:
      leaves  = [l for l in self.table.getLeaves() 
                 if l.getName(is_global_name='False') != NAME_COLUMN_STR]
      column = leaves[-1]
    column_name = column.getName(is_global_name=False)
    ROW_INDEX = None
    NEW_VALUE = None
    old_num_columns = self.table.numColumns()
    before_table = self.table.copy()
    deleted_column_name = column.getName(is_global_name=False)
    cmd_dict = {
                'target':  target,
                'command': 'Delete',
                'table_name': None,
                'column_name': column_name,
                'column_index': -1,
                'row_index': ROW_INDEX,
                'value': NEW_VALUE
               }
    self.table.processCommand(cmd_dict)
    expected_num_columns = old_num_columns - 1
    if target == "Table":
      expected_num_columns -= 1
    self.assertEqual(self.table.numColumns(), expected_num_columns)
    for r in range(self.table.numRows()):
      after_row = self.table.getRow(row_index=r)
      before_row = before_table.getRow(row_index=r)
      for k in after_row.keys():
        self.assertEqual(after_row[k], before_row[k])

  def testProcessCommandColumnDelete(self):
    #if IGNORE_TEST:
    #  return
    self._testProcessCommandColumnDelete("Table")
    self._testProcessCommandColumnDelete("Column")

  def testProcessCommandColumnRename(self):
    if IGNORE_TEST:
      return
    COLUMN_INDEX = 3
    column = self.table.columnFromIndex(COLUMN_INDEX)
    column_name = column.getName(is_global_name=False)
    ROW_INDEX = None
    NEW_VALUE = None
    NEW_COLUMN_NAME = "New_Name"
    cmd_dict = {
                'target':  'Column',
                'command': 'Rename',
                'table_name': None,
                'column_name': column_name,
                'column_index': COLUMN_INDEX,
                'row_index': ROW_INDEX,
                'args': [NEW_COLUMN_NAME],
                'value': NEW_VALUE,
               }
    old_num_columns = self.table.numColumns()
    self.table.processCommand(cmd_dict)
    self.assertEqual(self.table.numColumns(), old_num_columns)
    self.assertEqual(self.table.getColumns()[COLUMN_INDEX].getName(), NEW_COLUMN_NAME)

  def testGetHiddenColumns(self):
    if IGNORE_TEST:
      return
    columns = self.table.getColumns()
    for column in columns:
      self.table.hideChildren(column)
      self.assertTrue(column in self.table._hidden_children)
      self.table.hideChildren([column])
      self.assertTrue(column in self.table._hidden_children)
      self.assertEqual(len(self.table._hidden_children) , 1)
      self.assertEqual(self.table.getHiddenNodes(), [column])
      self.table.unhideChildren(column)
      self.assertEqual(len(self.table._hidden_children) , 0)

  def _testGetVisibleColumns(self, hide_names, expected_names):
    """
    Hides the list of names specified and then
    tests that the result is the expected_names.
    :param list-of-str hide_names:
    :param list-of-str expected_names:
    """
    if IGNORE_TEST:
      return
    node_dict = self.createNestedTable()
    table = node_dict["Table"]
    for name in hide_names:
      table.hideChildren(node_dict[name])
    visibles = table.getVisibleNodes()
    # Add two to account for name columns
    self.assertEqual(len(expected_names)+2, len(visibles))
    for name in expected_names:
      if name == NAME_COLUMN_STR:
        continue
      if not node_dict[name] in visibles:
        import pdb; pdb.set_trace()
      self.assertTrue(node_dict[name] in visibles)

  def testGetVisibleColumns(self):
    if IGNORE_TEST:
      return
    self._testGetVisibleColumns(["C"],
        ["A", "B", "Subtable", "D"])
    

if __name__ == '__main__':
    unittest.man()

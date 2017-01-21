'''Tests for UITable.'''

from mysite import settings
from scisheets.core.helpers.serialize_deserialize import serialize,  \
    deserialize
from scisheets.core.column import Column
from scisheets.core.table import NAME_COLUMN_STR
import ui_table as ui
from dt_table import DTTable
from django.test import TestCase  # Provides mocks
import json


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
NCOL = 4
NROW = 3
TABLE_NAME = "MY TABLE"
    

class TestUITable(TestCase):

  def setUp(self):
    self.table = DTTable.createRandomTable(TABLE_NAME,
        NROW, NCOL)

  def testCreateRandomTable(self):
    self.assertEqual(self.table.numRows(), NROW)
    self.assertEqual(self.table.numColumns(), NCOL+1)  # Include name col
    NCOLSTR = min(2, NCOL)
    new_table = DTTable.createRandomTable(TABLE_NAME,
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
    column_index = 3
    column = self.table.getChildAtPosition(column_index)
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
    self.table.processCommand(cmd_dict)
    self.assertEqual(int(self.table.getCell(ROW_INDEX, column_name)),
      NEW_VALUE)
    for c in range(self.table.numColumns()):
      self.assertEqual(before_table.getColumns()[c].getName(), 
          self.table.getColumns()[c].getName())
      for r in range(self.table.numRows()):
        if not (r == ROW_INDEX and c == column_index):
          self.assertEqual(before_table.getCell(r,c), 
              self.table.getCell(r,c))

  def testProcessCommandColumnDelete(self):
    COLUMN_INDEX = 3
    column = self.table.columnFromIndex(COLUMN_INDEX)
    column_name = column.getName(is_global_name=False)
    ROW_INDEX = None
    NEW_VALUE = None
    old_num_columns = self.table.numColumns()
    before_table = self.table.copy()
    deleted_column_name = self.table.getColumns()[COLUMN_INDEX].getName()
    cmd_dict = {
                'target':  'Column',
                'command': 'Delete',
                'table_name': None,
                'column_name': column_name,
                'column_index': COLUMN_INDEX,
                'row_index': ROW_INDEX,
                'value': NEW_VALUE
               }
    self.table.processCommand(cmd_dict)
    expected_num_columns = old_num_columns - 1
    self.assertEqual(self.table.numColumns(), expected_num_columns)
    for r in range(self.table.numRows()):
      after_row = self.table.getRow(row_index=r)
      before_row = before_table.getRow(row_index=r)
      for k in after_row.keys():
        self.assertEqual(after_row[k], before_row[k])

  def testProcessCommandColumnRename(self):
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

  def testAddEscapesToQuotes(self):
    list_of_str = ["xy", "x'y'"]
    mod_list_of_str = ui.UITable._addEscapesToQuotes(list_of_str)
    self.assertEqual(mod_list_of_str[1].index("\\"), 1)
    list_of_str = range(3)
    mod_list_of_str = ui.UITable._addEscapesToQuotes(list_of_str)
    self.assertTrue(list_of_str == mod_list_of_str)

  def testGetHiddenColumns(self):
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

  def testSerializeDeserialize(self):
    json_str = serialize(self.table)
    new_table = deserialize(json_str)
    self.assertTrue(self.table.isEquivalent(new_table))

  def createNestedTable(self):
    """
    Table
      A
      B
      Subtable
        C
        D
    :return dict: name, object pairs
    """
    table = ui.UITable("Table")
    result = {"Table": table}
    result["A"] = Column("A")
    table.addColumn(result["A"])
    result["B"] = Column("B")
    table.addColumn(result["B"])
    subtable = ui.UITable("Subtable")
    result["Subtable"] = subtable
    table.addChild(subtable)
    result["C"] = Column("C")
    subtable.addColumn(result["C"])
    result["D"] = Column("D")
    subtable.addColumn(result["D"])
    return result

  def _testGetVisibleColumns(self, hide_names, expected_names):
    """
    Hides the list of names specified and then
    tests that the result is the expected_names.
    :param list-of-str hide_names:
    :param list-of-str expected_names:
    """
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
    self._testGetVisibleColumns(["C"],
        ["A", "B", "Subtable", "D"])
    

if __name__ == '__main__':
    unittest.man()

'''Tests for UITable.'''

from mysite import settings
from scisheets.core.helpers.serialize_deserialize import serialize,  \
    deserialize
from scisheets.core.column import Column
from scisheets.core.table import NAME_COLUMN_STR, Table
from ui_table import UITable
from django.test import TestCase  # Provides mocks
import json
import random


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
IGNORE_TEST = False
LARGE_NUMBER = 1000
NCOL = 30
NROW = 3
TABLE_NAME = "MY_TABLE"
    

class TestUITableCommandsCell(TestCase):

  def testCellUpdate(self):
    if IGNORE_TEST:
      return
    table = UITable.createRandomTable(TABLE_NAME,
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


class TestUITableCommandsTableAndColumn(TestCase):

  def _getNode(self, target):
    """
    Gets a node appropriate for the target
    :param str target: Table or Column
    :return NamedTree node:
    """
    nodes = self.table.getAllNodes()
    if target == "Table":
      cls = Table
    else:
      cls = Column
    for _ in range(LARGE_NUMBER):
      index = random.randint(0,len(nodes)-1)
      node = nodes[index]
      if isinstance(node, cls):
        return node
    raise RuntimeError("Could not find a node.")

  def _testAppendAndInsert(self, target, command):
    """
    :param str target: Table or Column
    :param str command: 'Append' or 'Insert'
    """
    new_name = "NEW_COLUMN"
    node = self._getNode(target)
    node_name = node.getName()
    cmd_dict = {
                'target':  target,
                'command': command,
                'table_name': None,
                'column_name': node_name,
                'column_index': -1,
                'row_index': None,
                'value': None,
                'args': [new_name],
               }
    expected_columns = self.table.numColumns() + 1
    if command == "Append":
      expected_position = node.getPosition() + 1
    else:
      expected_position = node.getPosition()
    self.table.processCommand(cmd_dict)
    self.assertEqual(self.table.numColumns(), expected_columns)
    new_node = self.table.childFromName(new_name)
    self.assertIsNotNone(new_node)
    self.assertEqual(new_node.getPosition(), expected_position)

  def testAppendAndInsert(self):
    if IGNORE_TEST:
      return
    targets = ["Column", "Table"]
    commands = ["Append", "Insert"]
    for target in targets:
      for command in commands:
        self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
            NROW, NCOL, 0.3, prob_detach=0.2)
        self._testAppendAndInsert(target, command)

  def _testDelete(self, target):
    """
    :param str target: Table or Column
    """
    node = self._getNode(target)
    node_name = node.getName()
    old_num_nodes = len(self.table.getAllNodes())
    before_table = self.table.copy()
    cmd_dict = {
                'target':  target,
                'command': 'Delete',
                'table_name': None,
                'column_name': node_name,
                'column_index': -1,
                'row_index': None,
                'value': None,
               }
    expected_num_nodes = old_num_nodes - len(node.getAllNodes())
    self.table.processCommand(cmd_dict)
    self.assertEqual(len(self.table.getAllNodes()), expected_num_nodes)
    for r in range(self.table.numRows()):
      after_row = self.table.getRow(row_index=r)
      before_row = before_table.getRow(row_index=r)
      for k in after_row.keys():
        self.assertEqual(after_row[k], before_row[k])

  def testDelete(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    self._testDelete("Table")
    self._testDelete("Column")

  def _testFormula(self, column):
    """
    :param Column column: column to evaluate
    """
    colnm = column.getName(is_global_name=False)
    formula =   \
'''
a = 5
%s = range(a)
''' % colnm
    cmd_dict = {
                'target':  'Column',
                'command': 'Formula',
                'table_name': None,
                'column_name': column.getName(),
                'row_index': None,
                'value': None ,
                'args': [formula],
               }
    self.table.processCommand(cmd_dict)
    self.assertEqual(column.getFormula(), formula)
    self.assertEqual(column.getCells(), range(5))

  def testFormula(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    leaves = self.table.getDataColumns(is_recursive=True,
        is_attached=False)
    [self._testFormula(c) for c in leaves]

  def _testHide(self, target):
    """
    :param str target: Table or Column
    """
    node = self._getNode(target)
    nodes = node.getAllNodes()
    node_name = node.getName()
    cmd_dict = {
                'target':  target,
                'command': 'Hide',
                'table_name': None,
                'column_name': node_name,
                'column_index': -1,
                'row_index': None,
                'value': None,
               }
    self.table.processCommand(cmd_dict)
    [self.assertTrue(n in self.table.getHiddenNodes()) for n in nodes]

  def testHide(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    self._testHide("Column")
    self._testHide("Table")

  def _testMove(self, target):
    """
    :param str source: Table or Column
    :param str destination: Table or Column
    """
    source = self._getNode(target)
    destination = source
    while destination == source:
      destination = self._getNode(target)
    cmd_dict = {
                'target':  target,
                'command': 'Move',
                'table_name': None,
                'column_name': source.getName(),
                'column_index': -1,
                'row_index': None,
                'value': None,
                'args': [destination.getName()],
               }
    expected_position = destination.getPosition()
    expected_parent = destination.getParent()
    self.table.processCommand(cmd_dict)
    self.assertEqual(source.getPosition(), expected_position)
    self.assertEqual(source.getParent(), expected_parent)

  def testMove(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    self._testMove("Table")
    self._testMove("Column")

  def _testRename(self, target):
    node = self._getNode(target)
    current_name = node.getName(is_global_name=False)
    new_name = "New_Name"
    cmd_dict = {
                'target': target, 
                'command': 'Rename',
                'table_name': None,
                'column_name': current_name,
                'column_index': -1,
                'row_index': None,
                'args': [new_name],
                'value': None,
               }
    num_columns = self.table.numColumns()
    self.table.processCommand(cmd_dict)
    self.assertEqual(self.table.numColumns(), num_columns)
    new_node = self.table.childFromName(new_name)
    self.assertIsNotNone(new_name)

  def testRename(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    self._testRename("Table")
    self._testRename("Column")


class TestUITableFunctions(TestCase):

  def setUp(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)

  def testAddEscapesToQuotes(self):
    if IGNORE_TEST:
      return
    list_of_str = ["xy", "x'y'"]
    mod_list_of_str = UITable._addEscapesToQuotes(list_of_str)
    self.assertEqual(mod_list_of_str[1].index("\\"), 1)
    list_of_str = range(3)
    mod_list_of_str = UITable._addEscapesToQuotes(list_of_str)
    self.assertTrue(list_of_str == mod_list_of_str)

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

  def testSerializeDeserialize(self):
    if IGNORE_TEST:
      return
    json_str = serialize(self.table)
    new_table = deserialize(json_str)
    self.assertTrue(self.table.isEquivalent(new_table,
        is_exception=True))

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
    if IGNORE_TEST:
      return
    table = UITable("Table")
    result = {"Table": table}
    result["A"] = Column("A")
    table.addColumn(result["A"])
    result["B"] = Column("B")
    table.addColumn(result["B"])
    subtable = UITable("Subtable")
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


class TestUITableSheetCommands(TestCase):

  def setUp(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    

if __name__ == '__main__':
    unittest.man()

'''Tests for UITable.'''

from mysite import settings
from scisheets.core.helpers.serialize_deserialize import serialize,  \
    deserialize
from scisheets.core.column import Column
from scisheets.core.table import NAME_COLUMN_STR, Table
from scisheets.helpers.command_dict import CommandDict
from mysite.helpers.named_tree import GLOBAL_SEPARATOR
from scisheets.ui.ui_table import UITable
from django.test import TestCase  # Provides mocks
import json
import random


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
LARGE_NUMBER = 1000
NCOL = 30
NROW = 3
TABLE_NAME = "MY_TABLE"
IGNORE_TEST = False


########################################################
# Utility Functions And Classes
########################################################
def _getNode(table, target, excludes=None):
  """
  Gets a node of the specified class.
  :param Table table: Table to search
  :param str/Type target: Table or Column
  :param list-of-Node excludes: nodes to exclude
  :return NamedTree node:
  """
  if excludes is None:
    excludes = []
  nodes = table.getAllNodes()
  if isinstance(target, str):
    if target == "Table":
      cls = Table
    else:
      cls = Column
  else:
    cls = target
  for _ in range(LARGE_NUMBER):
    index = random.randint(0,len(nodes)-1)
    node = nodes[index]
    if table.isNameColumn(node):
      continue
    if isinstance(node, cls):
      if not node in excludes:
        return node
  raise RuntimeError("Could not find a node.")

def _evaluateMockedResponse(table, cmd_dict, 
    success=True, is_save=True):
  """
  Evaluates if the response from a mock is as expected.
  :param Table table:
  :param dict cmd_dict:
  :param bool success: value of success
  :param bool is_save: value of is_save
  """
  response, returned_is_save =  \
      table.processCommand(cmd_dict)
  return (response['success'] ==  success)  \
      and returned_is_save == is_save
    

########################################################
# Test Classes
########################################################
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
    cmd_dict = CommandDict.createCommandDict({
                'target':  'Cell',
                'command': 'Update',
                'table_name': None,
                'column_name': column_name,
                'row_index': ROW_INDEX,
                'value': NEW_VALUE
               })
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

  def setUp(self):
    self.cmd_dict = CommandDict.createCommandDict({
                    'target':  None,
                    'command': None,
                    'table_name': None,
                    'column_name': None,
                    'column_index': -1,
                    'row_index': None,
                    'value': None,
                   })

  def _testAppendAndInsert(self, target, command):
    """
    :param str target: Table or Column
    :param str command: 'Append' or 'Insert'
    """
    new_name = "NEW_COLUMN"
    node = _getNode(self.table, target)
    node_name = node.getName()
    self.cmd_dict['target'] = target
    self.cmd_dict['command'] = command
    self.cmd_dict['column_name'] = node_name
    self.cmd_dict['args'] = [new_name]
    expected_columns = self.table.numColumns() + 1
    if command == "Append":
      expected_position = node.getPosition() + 1
    else:
      expected_position = node.getPosition()
    self.table.processCommand(self.cmd_dict)
    self.assertEqual(self.table.numColumns(), expected_columns)
    new_node = self.table.childFromName(new_name, is_relative=False)
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
    node = _getNode(self.table, target)
    node_name = node.getName()
    old_num_nodes = len(self.table.getAllNodes())
    before_table = self.table.copy()
    self.cmd_dict['target'] = target
    self.cmd_dict['command'] = 'Delete'
    self.cmd_dict['column_name'] = node_name
    expected_num_nodes = old_num_nodes - len(node.getAllNodes())
    self.table.processCommand(self.cmd_dict)
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
    self.cmd_dict['target'] = 'Column'
    self.cmd_dict['command'] = 'Formula'
    self.cmd_dict['column_name'] = column.getName()
    self.cmd_dict['args'] = [formula]
    self.table.processCommand(self.cmd_dict)
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
    node = _getNode(self.table, target)
    nodes = node.getAllNodes()
    node_name = node.getName()
    self.cmd_dict['target'] = target
    self.cmd_dict['command'] = 'Hide'
    self.cmd_dict['column_name'] = node_name
    self.table.processCommand(self.cmd_dict)
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
    source = _getNode(self.table, target)
    destination = source
    while destination == source:
      destination = _getNode(self.table, target)
    self.cmd_dict['target'] = target
    self.cmd_dict['command'] = 'Move'
    self.cmd_dict['column_name'] = source.getName()
    self.cmd_dict['args'] = [destination.getName()]
    expected_position = destination.getPosition()
    expected_parent = destination.getParent()
    self.table.processCommand(self.cmd_dict)
    self.assertEqual(source.getPosition(), expected_position)
    self.assertEqual(source.getParent(), expected_parent)

  def testMove(self):
    #if IGNORE_TEST:
    #  return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    self._testMove("Table")
    self._testMove("Column")

  def _testRename(self, target):
    node = _getNode(self.table, target)
    current_name = node.getName(is_global_name=False)
    new_name = "New_Name"
    self.cmd_dict['target'] = target
    self.cmd_dict['command'] = 'Rename'
    self.cmd_dict['column_name'] = current_name
    self.cmd_dict['args'] = [new_name]
    num_columns = self.table.numColumns()
    self.table.processCommand(self.cmd_dict)
    self.assertEqual(self.table.numColumns(), num_columns)
    new_node = self.table.childFromName(new_name, is_relative=False)
    self.assertIsNotNone(new_name)

  def testRename(self):
    if IGNORE_TEST:
      return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    self._testRename("Table")
    self._testRename("Column")

  def _testTablize(self, target):
    node = _getNode(self.table, target)
    table_name = "%s_%d" % (node.getName(is_global_name=False),
        random.randint(1, 1000))
    if node.getParent() != node.getRoot(is_attached=False):
      full_table_name = "%s%s%s" % (node.getParent().getName(),
          GLOBAL_SEPARATOR, table_name)
    else:
      full_table_name = table_name
    self.cmd_dict['target'] = target
    self.cmd_dict['command'] = 'Tablize'
    self.cmd_dict['column_name'] = node.getName()
    self.cmd_dict['args'] = [table_name]
    expected = len(self.table.getAllNodes()) + 2
    self.table.processCommand(self.cmd_dict)
    self.assertEqual(len(self.table.getAllNodes()), expected)
    new_table = self.table.childFromName(full_table_name,
        is_relative=False)
    self.assertIsNotNone(new_table)
    new_node = new_table.childFromName(node.getName(is_global_name=False))
    self.assertTrue(node.isEquivalent(new_node, is_exception=True))

  def testTablize(self):
    #if IGNORE_TEST:
    #  return
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, NCOL, 0.3, prob_detach=0.2)
    for _ in range(1):
      self._testTablize("Table")
      self._testTablize("Column")


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

  def testIsEquivalentAndCopy(self):
    if IGNORE_TEST:
      return
    table_copy = self.table.copy()
    self.assertTrue(self.table.isEquivalent(table_copy))
    node = _getNode(self.table, "Column")
    node.removeTree()
    self.assertFalse(self.table.isEquivalent(table_copy))

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


class _PseudoVersionedGood(object):
  """
  Used to mock VersionedFile
  """

  def undo(self):
    return

  def redo(self):
    return

  def getFilepath(self):
    return None

  def getDirectory(self):
    return "."

  def getMaxVersions(self):
    return 1


class _PseudoVersionedBad(_PseudoVersionedGood):
  """
  Used to mock VersionedFile
  """

  def undo(self):
    raise RuntimeError()

  def redo(self):
    raise RuntimeError()


class TestUITableSheetCommands(TestCase):

  def setUp(self):
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        2, 10, 0.3, prob_detach=0.2)
    self.mock_dict = {}
    self.cmd_dict = CommandDict.createCommandDict({
                     'target': "Sheet",
                     'command': None,
                     'table_name': None,
                     'column_name': None,
                     'column_index': -1,
                     'row_index': None,
                     'args': [],
                     'value': None,
                    })

  def _evaluateMockedResponse(self, success=True, is_save=True):
    self.assertTrue(_evaluateMockedResponse(self.table,
        self.cmd_dict, success=success, is_save=is_save))

  def testExport(self):
    if IGNORE_TEST:
      return

    def pseudoExportGood(function_name="x",
        inputs=None, outputs=None, user_directory=None):
      self.mock_dict["pseudoExport"] = True
      return None
    def pseudoExportBad(function_name="x",
        inputs=None, outputs=None, user_directory=None):
      self.mock_dict["pseudoExport"] = True
      return "Error"
    def _getNodes(count):
      nodes = []
      while len(nodes) < count:
        excludes = list(nodes)
        node = _getNode(self.table, "Column", excludes=excludes)
        if not Table.isNameColumn(node):
          nodes.append(node)
      return nodes

    nodes = [n.getName(is_global_name=False) for n in _getNodes(4)]
    inputs = nodes[:2]
    outputs = nodes[2:]
    function_name = 'my_func'
    self.cmd_dict["command"] = "Export"
    args = [function_name, ', '.join(inputs), ', '.join(outputs)]
    self.cmd_dict["args"] = args
    # Successful export
    self.table.export = pseudoExportGood  # Mock the export function
    self._evaluateMockedResponse(success=True, is_save=True)
    # Unsuccessful export
    self.table.export = pseudoExportBad  # Mock the export function
    self._evaluateMockedResponse(success=False, is_save=False)

  def testRedo(self):
    if IGNORE_TEST:
      return
    self.cmd_dict["command"] = "Redo"
    self.table.setVersionedFile(_PseudoVersionedGood())
    self._evaluateMockedResponse(success=True, is_save=False)
    self.table.setVersionedFile(_PseudoVersionedBad())
    self._evaluateMockedResponse(success=False, is_save=False)

  def _testUnhide(self, target):
    #if IGNORE_TEST:
    #  return
    self.table.unhideAllChildren()
    self.cmd_dict["command"] = "Unhide"
    if target == "Column":
      node = _getNode(self.table, target)
      self.cmd_dict["target"] = "Column"
      self.cmd_dict["column_name"] = node.getName()
    elif target == "Table":
      node = _getNode(self.table, target)
      self.cmd_dict["target"] = target
      self.cmd_dict["column_name"] = node.getName()
    else:
      # Sheet
      self.cmd_dict["target"] = "Sheet"
      node = _getNode(self.table, "Column")
      self.cmd_dict["command"] = "UnhideAll"
    self.table.hideChildren([node])
    self.assertTrue(self.table.isHiddenChild(node))
    self._evaluateMockedResponse(success=True, is_save=True)
    self.assertFalse(self.table.isHiddenChild(node))

  def testUnhide(self):
    if IGNORE_TEST:
      return
    self._testUnhide("Column")
    self._testUnhide("Table")
    self._testUnhide("Sheet")

  def testUndo(self):
    if IGNORE_TEST:
      return
    self.cmd_dict["command"] = "Undo"
    self.table.setVersionedFile(_PseudoVersionedGood())
    self._evaluateMockedResponse(success=True, is_save=False)
    self.table.setVersionedFile(_PseudoVersionedBad())
    self._evaluateMockedResponse(success=False, is_save=False)


class TestUITableCommandsRow(TestCase):

  def setUp(self):
    self.table = UITable.createRandomHierarchicalTable(TABLE_NAME, 
        4, 10, 0.3, prob_detach=0.2)
    self.row_index = 1
    self.num_rows = self.table.numRows()
    self.cmd_dict = CommandDict.createCommandDict({
                     'target':  'Row',
                     'command': None,
                     'table_name': None,
                     'column_name': NAME_COLUMN_STR,
                     'column_index': None,
                     'args': [self.row_index],
                     'row_index': self.row_index,
                     'value': None,
                   })
    self.row_index_values = self.table.getRow(row_index=self.row_index)

  def _evaluateMockedResponse(self, success=True, is_save=True):
    self.assertTrue(_evaluateMockedResponse(self.table,
        self.cmd_dict, success=success, is_save=is_save))

  def testSimpleCommands(self):
    if IGNORE_TEST:
      return
    def pseudoRenameRow(row_index, new_name):
      return None
    def pseudoDeleteRow(rows):
      return None
    def pseudoAddRow(row, row_index):
      return None

    mocks = {"Move": [pseudoRenameRow, 'renameRow'],
             "Delete": [pseudoDeleteRow, 'deleteRow'],
             "Insert": [pseudoAddRow, 'addRow'],
             "Append": [pseudoAddRow, 'addRow'],
            }
    for command in mocks.keys():
      self.cmd_dict["command"] = command
      # Insert the mocks
      setattr(self.table, mocks[command][1], mocks[command][0])
      self._evaluateMockedResponse(success=True, is_save=True)


if __name__ == '__main__':
    unittest.man()

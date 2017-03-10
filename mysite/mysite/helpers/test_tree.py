'''Tests for Tree'''

import unittest
from mysite.helpers.tree import Node, Tree, PositionTree
from mysite.helpers.data_capture import DataCapture
from mysite.helpers.named_tree import NamedTree
import json
import os


NAME = "NAME1"
NAME2 = "NAME2"
NAME3 = "NAME3"
NAME4 = "NAME4"
NAME5 = "NAME5"
NEW_NAME = "XXYY"

IGNORE_TEST = False

#############################
# Helper Functions
#############################
def getCapture(filename):
  dc = DataCapture(filename)
  return dc.getData()


#############################
# Test classes
#############################
class TestNode(unittest.TestCase):

  def testAll(self):
    if IGNORE_TEST:
      return
    node = Node(NAME)
    self.assertEqual(node.getName(), NAME)
    node.setName(NAME2)
    self.assertEqual(node.getName(), NAME2)


class TestTree(unittest.TestCase):

  
  def setUp(self):
    self.root = Tree(NAME)
    self.tree2 = None
    self.tree3 = None
    self.tree4 = None

  def _AddChild(self, name):
    new_tree = Tree(name)
    self.root.addChild(new_tree)
    return new_tree

  def _createComplexTree(self):
    """
    Creates the following tree
      NAME1->NAME2->NAME4
      NAME1->NAME3
    """
    self.tree2 = self._AddChild(NAME2)
    self.tree3 = self._AddChild(NAME3)
    self.tree4 = Tree(NAME4)
    self.tree2.addChild(self.tree4)

  def testConstructor(self):
    if IGNORE_TEST:
      return
    self.assertEqual(self.root._name, NAME)
    self.assertEqual(len(self.root._children), 0)

  def testAddChild(self):
    if IGNORE_TEST:
      return
    new_tree = self._AddChild(NAME2)
    self.assertEqual(len(self.root._children), 1)
    self.assertEqual(self.root._children[0], new_tree)
    newer_tree = self._AddChild(NAME3)
    self.assertEqual(len(self.root._children), 2)
    self.assertEqual(self.root._children[1], newer_tree)

  def testAddChildComplex(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    self.assertTrue(self.tree4 in self.tree2.getChildren())

  def testRemoveChildSimple(self):
    if IGNORE_TEST:
      return
    new_tree = self._AddChild(NAME2)
    new_tree.removeTree()
    self.assertIsNone(new_tree._parent)
    self.assertEqual(len(self.root._children), 0)

  def testRemoveChildComplex(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    self.tree4.removeTree()
    self.assertIsNone(self.tree4._parent)
    self.assertEqual(len(self.tree2._children), 0)
    self.assertEqual(len(self.root._children), 2)

  def testGetRoot(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    self.assertEqual(self.tree2._children[0], self.tree4)
    root = self.tree4.getRoot()
    self.assertEqual(root, self.root)
    root = self.root.getRoot()
    self.assertEqual(root, self.root)
    root = self.tree3.getRoot()
    self.assertEqual(root, self.root)

  def testGetChildrenFromRoot(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    children = self.tree2.getChildren(is_from_root=False)
    self.assertEqual(children, [self.tree4])
    children = self.tree4.getChildren(is_from_root=True, 
        is_recursive=True)
    self.assertEqual(len(children), 3)
    self.assertFalse(self.root in children)
    self.assertTrue(self.tree2 in children)
    self.assertTrue(self.tree4 in children)

  def testGetChildrenFromSelf(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    children = self.tree2.getChildren(is_from_root=False)
    grandchildren = self.tree4.getChildren(is_from_root=False)
    self.assertEqual(len(children), 1)
    self.assertEqual(len(grandchildren), 0)
    self.assertTrue(self.tree4 in children)

  def testFindPathFromRoot(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    path = self.tree2.findPathFromRoot()
    self.assertEqual(path, [NAME, NAME2])
    path = self.tree4.findPathFromRoot()
    self.assertEqual(path, [NAME, NAME2, NAME4])

  def testFindName(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    trees = self.tree2.findChildrenWithName(NAME3, is_from_root=True)
    self.assertEqual(trees, [self.tree3])
    trees = self.tree2.findChildrenWithName(NAME3, is_from_root=False)
    self.assertEqual(trees, [])

  def _checkNodeLists(self, list1, list2):
    names1 = [l.getName() for l in list1]
    names2 = [l.getName() for l in list2]
    return set(names1) == set(names2)

  def testGetLeaves(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    leaves = self.tree2.getLeaves(is_from_root=True)
    self.assertTrue(self._checkNodeLists(leaves, [self.tree3, self.tree4]))
    leaves = self.tree2.getLeaves(is_from_root=False)
    self.assertTrue(self._checkNodeLists(leaves, [self.tree4]))

  def testToString(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    print_string = self.root.toString()
    self.assertTrue("%s->%s" % (NAME, NAME3) in print_string)
    self.assertTrue("%s->%s" % (NAME, NAME2) in print_string)
    self.assertTrue("%s->%s" % (NAME2, NAME4) in print_string)

  def testIsAlwaysLeaf(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    self.assertFalse(self.tree2.isAlwaysLeaf())

  def testCopy(self):
    if IGNORE_TEST:
      return
    new_tree = self.root.copy()
    self.assertTrue(self.root.isEquivalent(new_tree))


class TestPositionTree(unittest.TestCase):
  
  def setUp(self):
    self.root = PositionTree(NAME)
    self._createComplexTree()

  def _AddChild(self, name, position=None):
    new_tree = PositionTree(name)
    self.root.addChild(new_tree, position=position)
    return new_tree

  def _createComplexTree(self):
    """
    Creates the following tree
      0: NAME1->NAME3
      1: NAME1->NAME2->NAME4
    """
    self.tree2 = self._AddChild(NAME2, position=1)
    self.tree3 = self._AddChild(NAME3, position=0)
    self.tree4 = Tree(NAME4)
    self.tree2.addChild(self.tree4)

  def testAddChild(self):
    if IGNORE_TEST:
      return
    self.assertEqual(self.root._children[0], self.tree3)
    self.assertEqual(self.root._children[1], self.tree2)

  def testGetChildAtPosition(self):
    if IGNORE_TEST:
      return
    tree3 = self.root.getChildAtPosition(0)
    self.assertEqual(tree3, self.tree3)
    tree2 = self.root.getChildAtPosition(1)
    self.assertEqual(tree2, self.tree2)
    with self.assertRaises(ValueError):
      _ = self.root.getChildAtPosition(2)

  def testGetPosition(self):
    if IGNORE_TEST:
      return
    expected_position = self.root.getPositionOfChild(self.tree2)
    self.assertEqual(expected_position, self.tree2.getPosition())
    self.assertIsNone(self.root.getPosition())

  def testGetPositionOfChild(self):
    if IGNORE_TEST:
      return
    position = self.root.getPositionOfChild(self.tree2)
    self.assertEqual(position, 1)
    self.assertIsNone(self.root.getPositionOfChild(self.tree4))

  def testMoveChildToPosition(self):
    if IGNORE_TEST:
      return
    tree5 = PositionTree(NAME5)
    self.root.addChild(tree5)
    new_position = 0
    self.root.moveChildToPosition(self.tree2, new_position)
    self.assertEqual(self.root._children[0], self.tree2)
    # Make sure it works if nothing is moved
    new_position = 0
    self.root.moveChildToPosition(self.tree2, new_position)
    self.assertEqual(self.root._children[0], self.tree2)
    # Move an end tree
    new_position = 0
    self.root.moveChildToPosition(tree5, new_position)
    self.assertEqual(self.root._children[0], tree5)

  def testToString(self):
    if IGNORE_TEST:
      return
    tree5 = PositionTree(NAME5)
    self.root.addChild(tree5)
    result = self.root.toString()
    self.assertTrue("2: ->NAME5" in result)
    self.assertEqual(result.count('->'), 4)

  def testIsRoot(self):
    if IGNORE_TEST:
      return
    self.assertTrue(self.root.isRoot())
    new_tree = Tree("DUMMY_TREE")
    self.root.addChild(new_tree)
    self.assertFalse(new_tree.isRoot())
    self.assertTrue(self.root.isRoot())

  # TODO: Delete since this is testing Table?
  def testIsEquivalent(self):
    if IGNORE_TEST:
      return
    [table, other_table] = getCapture("test_table_1")
    result = super(NamedTree, table).isEquivalent(other_table)
    self.assertTrue(result)

  def testValidateTree(self):
    self.tree2 = self._AddChild(NEW_NAME)
    with self.assertRaises(RuntimeError):
      self.tree2 = self._AddChild(NEW_NAME)

    

if __name__ == '__main__':
    unittest.main()

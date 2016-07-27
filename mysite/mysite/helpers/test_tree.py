'''Tests for Tree'''

import unittest
from tree import Node, Tree, PositionTree
import json
import os


NAME = "NAME1"
NAME2 = "NAME2"
NAME3 = "NAME3"
NAME4 = "NAME4"
NAME5 = "NAME5"


class TestNode(unittest.TestCase):

  def testAll(self):
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
    self.assertEqual(self.root._name, NAME)
    self.assertEqual(len(self.root._children), 0)

  def testAddChild(self):
    new_tree = self._AddChild(NAME2)
    self.assertEqual(len(self.root._children), 1)
    self.assertEqual(self.root._children[0], new_tree)
    newer_tree = self._AddChild(NAME3)
    self.assertEqual(len(self.root._children), 2)
    self.assertEqual(self.root._children[1], newer_tree)

  def testAddChildComplex(self):
    self._createComplexTree()
    self.assertTrue(self.tree4 in self.tree2.getChildren())

  def testRemoveChildSimple(self):
    new_tree = self._AddChild(NAME2)
    new_tree.removeTree()
    self.assertIsNone(new_tree._parent)
    self.assertEqual(len(self.root._children), 0)

  def testRemoveChildComplex(self):
    self._createComplexTree()
    self.tree4.removeTree()
    self.assertIsNone(self.tree4._parent)
    self.assertEqual(len(self.tree2._children), 0)
    self.assertEqual(len(self.root._children), 2)

  def testGetRoot(self):
    self._createComplexTree()
    self.assertEqual(self.tree2._children[0], self.tree4)
    root = self.tree4.getRoot()
    self.assertEqual(root, self.root)
    root = self.root.getRoot()
    self.assertEqual(root, self.root)
    root = self.tree3.getRoot()
    self.assertEqual(root, self.root)

  def testGetChildrenFromRoot(self):
    self._createComplexTree()
    children = self.tree2.getChildren(is_from_root=False)
    self.assertEqual(children, [self.tree4])
    children = self.tree4.getChildren(is_from_root=True, 
        is_recursive=True)
    self.assertEqual(len(children), 4)
    self.assertTrue(self.root in children)
    self.assertTrue(self.tree2 in children)
    self.assertTrue(self.tree4 in children)

  def testGetChildrenFromSelf(self):
    self._createComplexTree()
    children = self.tree2.getChildren(is_from_root=False)
    grandchildren = self.tree4.getChildren(is_from_root=False)
    self.assertEqual(len(children), 1)
    self.assertEqual(len(grandchildren), 0)
    self.assertTrue(self.tree4 in children)

  def testFindPathFromRoot(self):
    self._createComplexTree()
    path = self.tree2.findPathFromRoot()
    self.assertEqual(path, [NAME, NAME2])
    path = self.tree4.findPathFromRoot()
    self.assertEqual(path, [NAME, NAME2, NAME4])

  def testFindName(self):
    self._createComplexTree()
    trees = self.tree2.findChildrenWithName(NAME3, is_from_root=True)
    self.assertEqual(trees, [self.tree3])
    trees = self.tree2.findChildrenWithName(NAME3, is_from_root=False)
    self.assertEqual(trees, [])
  

  def testGetLeaves(self):
    self._createComplexTree()
    leaves = self.tree2.getLeaves(is_from_root=True)
    self.assertEqual(leaves, [self.tree3, self.tree4])
    leaves = self.tree2.getLeaves(is_from_root=False)
    self.assertEqual(leaves, [self.tree4])

  def testToString(self):
    self._createComplexTree()
    print_string = self.root.toString()
    self.assertTrue("%s->%s" % (NAME, NAME3) in print_string)
    self.assertTrue("%s->%s" % (NAME, NAME2) in print_string)
    self.assertTrue("%s->%s" % (NAME2, NAME4) in print_string)


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
    self.assertEqual(self.root._children[0], self.tree3)
    self.assertEqual(self.root._children[1], self.tree2)

  def testGetChildAtPosition(self):
    tree3 = self.root.getChildAtPosition(0)
    self.assertEqual(tree3, self.tree3)
    tree2 = self.root.getChildAtPosition(1)
    self.assertEqual(tree2, self.tree2)
    with self.assertRaises(ValueError):
      _ = self.root.getChildAtPosition(2)

  def testGetPositionOfChild(self):
    position = self.root.getPositionOfChild(self.tree2)
    self.assertEqual(position, 1)
    self.assertIsNone(self.root.getPositionOfChild(self.tree4))

  def testMoveChildToPosition(self):
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

  def testtoString(self):
    tree5 = PositionTree(NAME5)
    self.root.addChild(tree5)
    result = self.root.toString()
    self.assertTrue("2: ->NAME5" in result)
    self.assertEqual(result.count('->'), 4)
    

if __name__ == '__main__':
    unittest.main()

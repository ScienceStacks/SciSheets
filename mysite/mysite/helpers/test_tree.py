'''Tests for Tree'''

import unittest
from tree import Tree
import json
import os


NAME = "NAME1"
NAME2 = "NAME2"
NAME3 = "NAME3"
NAME4 = "NAME4"


class TestTree(unittest.TestCase):

  
  def setUp(self):
    self.root = Tree(NAME)
    self.tree2 = None
    self.tree3 = None
    self.tree4 = None

  def testConstructor(self):
    self.assertEqual(self.root._name, NAME)
    self.assertEqual(len(self.root._children), 0)

  def _AddChild(self, name):
    new_tree = Tree(name)
    self.root.addChild(new_tree)
    return new_tree

  def testAddChild(self):
    new_tree = self._AddChild(NAME2)
    self.assertEqual(len(self.root._children), 1)
    self.assertEqual(self.root._children[0], new_tree)
    newer_tree = self._AddChild(NAME3)
    self.assertEqual(len(self.root._children), 2)
    self.assertEqual(self.root._children[1], newer_tree)

  def testRemoveChildSimple(self):
    new_tree = self._AddChild(NAME2)
    new_tree.removeMember()
    self.assertIsNone(new_tree._parent)
    self.assertEqual(len(self.root._children), 0)

  def testRemoveChildComplex(self):
    new_tree = self._AddChild(NAME2)
    self._AddChild(NAME3)
    self.assertEqual(len(self.root._children), 2)
    new_tree.removeMember()
    self.assertIsNone(new_tree._parent)
    self.assertEqual(len(self.root._children), 1)

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

  def testGetRoot(self):
    self._createComplexTree()
    self.assertEqual(self.tree2._children[0], self.tree4)
    root = self.tree4.getRoot()
    self.assertEqual(root, self.root)

  def testGetMembersFromRoot(self):
    self._createComplexTree()
    child_members = self.tree2.getMembers(is_from_root=True)
    grandchild_members = self.tree4.getMembers(is_from_root=True)
    self.assertEqual(child_members, grandchild_members)
    self.assertEqual(len(child_members), 4)
    self.assertTrue(self.root in child_members)
    self.assertTrue(self.tree2 in child_members)
    self.assertTrue(self.tree4 in child_members)

  def testGetMembersFromSelf(self):
    self._createComplexTree()
    child_members = self.tree2.getMembers(is_from_root=False)
    grandchild_members = self.tree4.getMembers(is_from_root=False)
    self.assertEqual(len(child_members), 2)
    self.assertEqual(len(grandchild_members), 1)
    self.assertTrue(self.tree2 in child_members)
    self.assertTrue(self.tree4 in child_members)

  def testFindPathFromRoot(self):
    self._createComplexTree()
    path = self.tree2.findPathFromRoot()
    self.assertEqual(path, [NAME, NAME2])
    path = self.tree4.findPathFromRoot()
    self.assertEqual(path, [NAME, NAME2, NAME4])

  def testFindName(self):
    self._createComplexTree()
    trees = self.tree2.findName(NAME3, is_from_root=True)
    self.assertEqual(trees, [self.tree3])
    trees = self.tree2.findName(NAME3, is_from_root=False)
    self.assertEqual(trees, [])
  

  def testGetLeaves(self):
    self._createComplexTree()
    leaves = self.tree2.getLeaves(is_from_root=True)
    self.assertEqual(leaves, [self.tree3, self.tree4])
    leaves = self.tree2.getLeaves(is_from_root=False)
    self.assertEqual(leaves, [self.tree4])
    


if __name__ == '__main__':
    unittest.main()

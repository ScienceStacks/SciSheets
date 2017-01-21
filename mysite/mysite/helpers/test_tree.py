'''Tests for Tree'''

import unittest
from tree import Node, Tree, PositionTree, TreeIterator
from scisheets.core.table import Table
from scisheets.core.column import Column
from data_capture import DataCapture
from named_tree import NamedTree
import json
import os


NAME = "NAME1"
NAME2 = "NAME2"
NAME3 = "NAME3"
NAME4 = "NAME4"
NAME5 = "NAME5"
NEW_NAME = "XXYY"
COMPLEX_TREE_LIST = [NAME2, NAME4, NAME3]

IGNORE_TEST = False

#############################
# Helper Functions
#############################
def getCapture(filename):
  dc = DataCapture(filename)
  return dc.getData()

def _verifyComplexTreeDepthFirstList(dfl, root_name=NEW_NAME):
  """
  Verifies that the depth first list for a complex tree
  produced by _createComplexTree
  :param list-of-str dfl: depth first list
  :param str root_name: name of the root
  """
  names = [root_name]
  names.extend(COMPLEX_TREE_LIST)
  last_pos = -1
  for name in names:
    pos = dfl.index(name)
    if not last_pos < pos:
      import pdb; pdb.set_trace()
    if not (last_pos < pos):
      raise Exception("Does not verify for position %d" % pos)


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

  def _createComplexTree(self, root_name=NAME):
    """
    Creates the following tree
      NAME1->NAME2->NAME4
      NAME1->NAME3
    :param str root_name: name of the root node
    """
    self.tree2 = self._AddChild(NAME2)
    self.tree3 = self._AddChild(NAME3)
    self.tree4 = Tree(NAME4)
    self.tree2.addChild(self.tree4)
    self.root.setName(root_name)

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

  def testGetAllNodes(self):
    """
      NAME1->NAME2->NAME4
      NAME1->NAME3
    """
    if IGNORE_TEST:
      return
    root = Tree(NEW_NAME)
    nodes = root.getAllNodes()
    self.assertEqual(len(nodes), 1)
    self.assertEqual(nodes[0]._name, NEW_NAME)
    self._createComplexTree()
    names = [n._name for n in self.root.getAllNodes()]
    _verifyComplexTreeDepthFirstList(names, root_name=NAME)

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
    """
    NAME1:
      NAME2
        NAME4
          NAME4.1
          NAME4.2
      NAME3
    """
    if IGNORE_TEST:
      return
    self._createComplexTree()
    self.tree4.addChild(Tree(NAME4 + ".1"))
    self.tree4.addChild(Tree(NAME4 + ".2"))
    children = self.tree2.getChildren(is_from_root=False,
        is_recursive=True)
    grandchildren = self.tree4.getChildren(is_from_root=False)
    self.assertEqual(len(children), 3)
    self.assertEqual(len(grandchildren), 2)
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
    self.root.setName(NEW_NAME)
    print_string = self.root.toString()
    _verifyComplexTreeDepthFirstList(print_string)

  def testIsAlwaysLeaf(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    self.assertFalse(self.tree2.isAlwaysLeaf())

  def testCopy(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    new_tree = self.root.copy()
    self.assertTrue(self.root.isEquivalent(new_tree))

  def testComplexCopy(self):
    if IGNORE_TEST:
      return
    tree = Tree.createRandomTree(100, 0.8)
    new_tree = tree.copy()
    self.assertTrue(tree.isEquivalent(new_tree))

  def testGetReverseOrderListOfNodes(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    reverse_nodes = self.root.getReverseOrderListOfNodes()
    forward_nodes = [n for n in self.root]
    forward_nodes.reverse()
    self.assertEqual(forward_nodes, reverse_nodes)

  def _testRandomTrees(self, leaf_cls=None, nonleaf_cls=None,
      tree_test=lambda x: True):
    num_nodes = [3, 100, 20, 1]
    branching_probabilities = [0.5, 0.2, 0.8]
    for nn in num_nodes:
      for pp in branching_probabilities:
         tree = Tree.createRandomTree(nn, pp, seed=0.3,
             leaf_cls=leaf_cls, nonleaf_cls=nonleaf_cls)
         nodes = [n for n in tree]
         diff = abs(len(nodes) - nn)
         if diff > 1:
           import pdb; pdb.set_trace()
         self.assertTrue(diff < 2)
         if not tree_test(tree):
           import pdb; pdb.set_trace()
         self.assertTrue(tree_test(tree))

  def testRandomTrees(self):
    if IGNORE_TEST:
      return
    self._testRandomTrees()

  def testRandomTreeWithTableAndColumns(self):
    if IGNORE_TEST:
      return
    tree_test = lambda x: all([isinstance(l, Column) 
                               for l in x.getLeaves()])
    self._testRandomTrees(nonleaf_cls=Table, leaf_cls=Column,
        tree_test=tree_test)
    self._testRandomTrees(leaf_cls=Column)
    self._testRandomTrees(leaf_cls=Table)
    self._testRandomTrees(nonleaf_cls=Table)

  def testGetUniqueName(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    unique_name = self.tree4.getUniqueName()
    self.assertEqual(unique_name, 'NAME1.NAME2.NAME4')

  def testGetChldrenAsDict(self):
    if IGNORE_TEST:
      return
    self._createComplexTree()
    children_dict = self.root.getChildrenBreadthFirst()
    self.assertEqual(children_dict["node"], self.root)
    self.assertEqual(len(children_dict["children"]), 2)
    #
    children_dict = self.root.getChildrenBreadthFirst(
        excludes=[self.tree2])
    self.assertEqual(children_dict["node"], self.root)
    self.assertEqual(len(children_dict["children"]), 1)
    #
    children_dict = self.root.getChildrenBreadthFirst(
        includes=[self.root, self.tree2])
    self.assertEqual(children_dict["node"], self.root)
    self.assertEqual(len(children_dict["children"]), 1)
    #
    children_dict = self.root.getChildrenBreadthFirst(
        includes=[self.tree2])
    self.assertEqual(len(children_dict.keys()), 0)


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
    self.tree4 = PositionTree(NAME4)
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

  def testMoveChildToOtherchild(self):
    """
    Existing tree
      NAME1
        NAME3
        NAME2
          NAME4
    New tree
      NAME1
        NAME4
        NAME3
        NAME2
    """
    if IGNORE_TEST:
     return
    self.root.moveChildToOtherchild(self.tree4, self.tree3)
    self.assertEqual(self.root.getChildAtPosition(0), self.tree4)

  def testMoveChildToOtherchild2(self):
    """
    Existing tree
      NAME1
        NAME3
        NAME2
          NAME4
    New tree
      NAME1
        NAME2
          NAME4
        NAME3
    """
    if IGNORE_TEST:
     return
    self.root.moveChildToOtherchild(self.tree3, self.tree2)
    self.assertEqual(self.root.getChildAtPosition(0), self.tree2)

  def testIsRoot(self):
    if IGNORE_TEST:
      return
    self.assertTrue(self.root.isRoot())
    new_tree = Tree("DUMMY_TREE")
    self.root.addChild(new_tree)
    self.assertFalse(new_tree.isRoot())
    self.assertTrue(self.root.isRoot())

  def testValidateTree(self):
    if IGNORE_TEST:
      return
    self.tree2 = self._AddChild(NEW_NAME)
    with self.assertRaises(RuntimeError):
      self.tree2 = self._AddChild(NEW_NAME)

  def testIter(self):
    if IGNORE_TEST:
      return
    self.assertTrue(isinstance(iter(self.root), TreeIterator))
    iterator = iter(self.root)
    self.assertTrue(isinstance(next(iterator), Tree))

  def testCreateRandomTree(self):
    if IGNORE_TEST:
      return
    num_nodes = 5
    tree = Tree.createRandomTree(num_nodes, 0.1)
    self.assertEqual(len(tree.getAllNodes()), num_nodes)
    self.assertEqual(len(tree.getChildren()), num_nodes-1)
    tree = Tree.createRandomTree(1, 0.1)
    self.assertEqual(len(tree.getAllNodes()), 1)
    tree = Tree.createRandomTree(2, 0.1)
    self.assertEqual(len(tree.getAllNodes()), 2)
    tree = Tree.createRandomTree(num_nodes, 0.99)
    self.assertEqual(len(tree.getAllNodes()), num_nodes)
    num_nodes = 500
    tree = Tree.createRandomTree(num_nodes, 0.1)
    tree.validateTree()

  def testFindLeavesInNodes(self):
    num_nodes = 50
    tree1 = Tree.createRandomTree(num_nodes, 0.2)
    tree2 = Tree.createRandomTree(num_nodes, 0.2)
    expected = tree1.getLeaves()
    expected.extend(tree2.getLeaves())
    expected = set(expected)
    nodes = tree1.getAllNodes()
    nodes.extend(tree2.getAllNodes())
    actual = set(Tree.findLeavesInNodes(nodes))
    self.assertEqual(expected.difference(actual),
        actual.difference(expected))

  def testFindRootsInNodes(self):
    num_nodes = 5
    tree1 = Tree.createRandomTree(num_nodes, 0.2)
    tree2 = Tree.createRandomTree(num_nodes, 0.2)
    nodes = tree1.getAllNodes()
    nodes.extend(tree2.getAllNodes())
    roots = Tree.findRootsInNodes(nodes)
    self.assertEqual(len(roots), 2)
    for tree in [tree1, tree2]:
      self.assertTrue(tree in roots)
    tree1.addChild(tree2)
    roots = Tree.findRootsInNodes(nodes)
    self.assertEqual(roots, [tree1])

    

if __name__ == '__main__':
    unittest.main()

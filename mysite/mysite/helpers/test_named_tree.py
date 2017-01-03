'''Tests for ColumnContainer'''

from named_tree import NamedTree, ROOT_NAME, FLATTEN_SEPARATOR
import unittest


# Constants
CHILD = "DUMMY_CHILD"
CHILD1 = "DUMMY1_CHILD"
CHILD2 = "DUMMY2_CHILD"
CHILD3 = "DUMMY3_CHILD"
CHILD4 = "DUMMY4_CHILD"
SUBPARENT = "Subparent"
PARENT = 'DUMMY'

IGNORE_TEST = False


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestNamedTree(unittest.TestCase):

  def setUp(self):
    """
    root(DUMMY):
      root_child(DUMMY1_CHILD)
      (DUMMY2_CHILD)
      (DUMMY3_CHILD)
      subparent(Subparent)
        subparent_child(DUMMY4_CHILD)
    """
    self.root = NamedTree(PARENT)
    self.root_child = NamedTree(CHILD1)
    self.root.addChild(self.root_child)
    self.root.addChild(NamedTree(CHILD2))
    self.root.addChild(NamedTree(CHILD3))
    self.subparent = NamedTree(SUBPARENT)
    self.root.addChild(self.subparent)
    self.subparent_child = NamedTree(CHILD4)
    self.subparent.addChild(self.subparent_child)
    self.subparent_child_name = CHILD4
    self.children = self.root.getChildren()

  def testCreateGlobalName(self):
    if IGNORE_TEST:
     return
    global_name = self.root.createGlobalName(self.root_child)
    self.assertEqual(global_name, CHILD1)
    global_name = self.root.createGlobalName(self.subparent_child)
    expected_name = ".".join([SUBPARENT, self.subparent_child_name])
    self.assertEqual(global_name, expected_name)

  def testGlobalName(self):
    if IGNORE_TEST:
     return
    global_name = self.root.globalName(SUBPARENT, is_relative=True)
    self.assertEqual(global_name, SUBPARENT)
    global_name = self.root.globalName(SUBPARENT, is_relative=False)
    self.assertEqual(global_name, SUBPARENT)
    global_name = self.subparent.globalName(self.subparent_child_name,
                                            is_relative=True)
    expected = ".".join([SUBPARENT, self.subparent_child_name])
    self.assertEqual(global_name, expected)
    global_name = self.subparent.globalName(global_name,
                                            is_relative=False)
    self.assertEqual(global_name, expected)
    

  def testRelativeNameToGlobalName(self):
    if IGNORE_TEST:
      return
    global_name =  \
        self.root.globalName(self.subparent_child.getName(), 
                                             is_relative=True)
    expected_name = self.subparent_child.getName()
    self.assertEqual(global_name, expected_name)
    global_name = self.root.globalName(global_name, is_relative=False)
    expected_name = self.subparent_child.getName()
    self.assertEqual(global_name, expected_name)

  def testChildFromName(self):
    if IGNORE_TEST:
     return
    global_name = self.root.createGlobalName(self.subparent_child)
    child = self.root.childFromName(global_name, is_relative=False)
    self.assertEqual(child, self.subparent_child)
    subparent = self.root.childFromName(SUBPARENT, is_relative=True)
    self.assertTrue(subparent, self.subparent)
    child = self.subparent.childFromName(self.subparent_child_name, 
                                      is_relative=True)
    self.assertEqual(child, self.subparent_child)

  def testGetName(self):
    if IGNORE_TEST:
      return
    name = self.root.getName(is_global_name=False)
    self.assertEqual(name, PARENT)
    name = self.root.getName(is_global_name=True)
    self.assertEqual(name, ROOT_NAME)
    name = self.root_child.getName()
    self.assertEqual(name, self.root_child._name)
    name = self.subparent_child.getName(is_global_name=False)
    self.assertEqual(name, self.subparent_child_name)
    expected = ".".join([SUBPARENT, self.subparent_child_name])
    name = self.subparent_child.getName(is_global_name=True)
    self.assertEqual(name, expected)

  def testSetName(self):
    if IGNORE_TEST:
     return
    self.assertIsNone(self.root.setName("newTable"))
    self.assertIsNotNone(self.root.setName("new Table"))

  def testCreateSubstitutedChildrenDict(self):
    if IGNORE_TEST:
      return
    nodes = [self.root, self.root_child, self.subparent, self.subparent_child]
    substitution_dict = {n: n.getName() for n in nodes}
    result = self.root.createSubstitutedChildrenDict(substitution_dict)
    self.assertEqual(result["name"], self.root.getName())
    self.assertEqual(result["label"], self.root._name)
    self.assertEqual(len(result["children"]), 4)
    result = self.root.createSubstitutedChildrenDict(
        substitution_dict,
        excludes=[self.root_child])
    self.assertEqual(result["name"], self.root.getName())
    self.assertEqual(result["label"], self.root._name)
    self.assertEqual(len(result["children"]), 3)

  def testFlattenAttached(self):
    """
    Should produce

    root(DUMMY):
      DUMMY__DUMMY1_CHILD
      DUMMY__DUMMY2_CHILD
      DUMMY__DUMMY3_CHILD
      DUMMY__Subparent__DUMMY4_CHILD
    """
    tree_list = self.root.flatten()
    new_tree = tree_list[0]
    expected_names = [CHILD1, CHILD2, CHILD3, 
        "%s%s%s" % (SUBPARENT, FLATTEN_SEPARATOR, CHILD4)]
    names = [l.getName(is_global_name=False) 
             for l in new_tree.getLeaves()]
    self.assertEqual(set(expected_names), set(names))

  def testFlattenDetached(self):
    """
    Should produce

    root(DUMMY):
      DUMMY__DUMMY1_CHILD
      DUMMY__DUMMY2_CHILD
      DUMMY__DUMMY3_CHILD
      DUMMY__Subparent__DUMMY4_CHILD
    """
    self.subparent.setIsAttached(False)
    tree_list = self.root.flatten()
    flat_tree = tree_list[0]
    expected_names = [CHILD1, CHILD2, CHILD3, CHILD4]
    names = [l.getName(is_global_name=False) 
             for l in flat_tree.getLeaves()]
    self.assertEqual(set(expected_names[:-1]), set(names))
    name = "%s%s%s" % (self.root._name, FLATTEN_SEPARATOR,
        SUBPARENT)   
    self.assertEqual(name, tree_list[1]._name)
    child = tree_list[1].getChildren()[0]
    self.assertEqual(expected_names[-1], child._name)

  def testUnflattenOneTree(self):
    tree_list = self.root.flatten()
    new_tree = NamedTree.unflatten(tree_list)
    self.assertTrue(self.root.isEquivalent(new_tree))

  def testUnflattenTwoTrees(self):
    self.subparent.setIsAttached(False)
    tree_list = self.root.flatten()
    new_tree = NamedTree.unflatten(tree_list)
    self.assertTrue(self.root.isEquivalent(new_tree))

  # TODO: Once record position of detached tree
  #       test for correctness with detached trees
  def testUnflattenManyTrees(self):
    tree = NamedTree.createRandomNamedTree(20, 0.5,
        prob_detach=0.0)
    tree_list = tree.flatten()
    new_tree = NamedTree.unflatten(tree_list)
    self.assertTrue(tree.isEquivalent(new_tree))


if __name__ == '__main__':
  unittest.main()

'''Tests for ColumnContainer'''

from named_tree import NamedTree, ROOT_NAME
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
    name = self.root.getName(is_node_name=True)
    self.assertEqual(name, PARENT)
    name = self.root.getName(is_global_name=True)
    self.assertEqual(name, ROOT_NAME)
    name = self.root_child.getName()
    self.assertEqual(name, self.root_child._name)
    name = self.subparent_child.getName()
    self.assertEqual(name, self.subparent_child_name)
    expected = ".".join([SUBPARENT, self.subparent_child_name])
    name = self.subparent_child.getName(is_global_name=True)
    self.assertEqual(name, expected)

  def testSetName(self):
    if IGNORE_TEST:
     return
    self.assertIsNone(self.root.setName("newTable"))
    self.assertIsNotNone(self.root.setName("new Table"))
    

if __name__ == '__main__':
  unittest.main()

'''Tests for ColumnContainer'''

from named_tree import NamedTree, ROOT_NAME, FLATTEN_SEPARATOR,  \
    NodeName, GLOBAL_SEPARATOR
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


def _setup(o):
  """
  root(DUMMY):
    root_child(DUMMY1_CHILD)
    (DUMMY2_CHILD)
    (DUMMY3_CHILD)
    subparent(Subparent)
      subparent_child(DUMMY4_CHILD)
  """
  o.root = NamedTree(PARENT)
  o.root_child = NamedTree(CHILD1)
  o.root.addChild(o.root_child)
  o.root.addChild(NamedTree(CHILD2))
  o.root.addChild(NamedTree(CHILD3))
  o.subparent = NamedTree(SUBPARENT)
  o.root.addChild(o.subparent)
  o.subparent_child = NamedTree(CHILD4)
  o.subparent.addChild(o.subparent_child)
  o.subparent_child_name = CHILD4
  o.children = o.root.getChildren()


#############################
# Tests
#############################
class TestNodeNode(unittest.TestCase):

  def setUp(self):
    _setup(self)

  def testGlobalName(self):
    if IGNORE_TEST:
     return
    root_node_name = NodeName(self.root)
    self.assertEqual(root_node_name.get(), ROOT_NAME)
    self.assertEqual(root_node_name.get(is_global=False),  self.root._name)
    subparent_node_name = NodeName(self.subparent)
    self.assertEqual(subparent_node_name.get(), SUBPARENT)
    child4_node_name = NodeName(self.subparent_child)
    expected = "%s%s%s" % (SUBPARENT, GLOBAL_SEPARATOR, CHILD4)
    self.assertEqual(child4_node_name.get(), expected)

  def testFactory(self):
    child4_node_str = NodeName.factory(self.subparent_child)
    expected = "%s%s%s" % (SUBPARENT, GLOBAL_SEPARATOR, CHILD4)
    self.assertEqual(child4_node_str, expected)


# pylint: disable=W0212,C0111,R0904
class TestNamedTree(unittest.TestCase):

  def setUp(self):
    _setup(self)

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

  def testFlattenAttached(self):
    """
    Should produce

    root(DUMMY):
      DUMMY__DUMMY1_CHILD
      DUMMY__DUMMY2_CHILD
      DUMMY__DUMMY3_CHILD
      DUMMY__Subparent__DUMMY4_CHILD
    """
    if IGNORE_TEST:
     return
    element_list = self.root.flatten()
    new_tree = element_list[0].tree
    expected_names = [CHILD1, CHILD2, CHILD3, 
        "%s%s%s" % (SUBPARENT, FLATTEN_SEPARATOR, CHILD4)]
    names = [l.getName(is_global_name=False) 
             for l in new_tree.getLeaves()]
    self.assertEqual(set(expected_names), set(names))

  def testDetachTreesSimple(self):
    """
    Should produce

    root(DUMMY):
      DUMMY__DUMMY1_CHILD
      DUMMY__DUMMY2_CHILD
      DUMMY__DUMMY3_CHILD
      DUMMY__Subparent__DUMMY4_CHILD
    """
    if IGNORE_TEST:
     return
    self.subparent.setIsAttached(False)
    elements = self.root._detachTrees()
    first_tree = elements[0].tree
    expected_names = [CHILD1, CHILD2, CHILD3, CHILD4]
    names = [l.getName(is_global_name=False) 
             for l in first_tree.getChildren()]
    self.assertEqual(set(expected_names[:-1]), set(names))
    name = "%s%s%s" % (self.root._name, FLATTEN_SEPARATOR,
        SUBPARENT)   
    self.assertEqual(name, elements[1].tree._name)
    child = elements[1].tree.getChildren()[0]
    self.assertEqual(expected_names[-1], child._name)

  def testDetachTreesRandom(self):
    if IGNORE_TEST:
      return
    tree = NamedTree.createRandomNamedTree(300, 0.5,
        prob_detach=0.2)
    elements = tree._detachTrees()
    detached = [c for c in tree.getAllNodes() if not c.isAttached()]
    expected_num = len(detached) + 1
    self.assertEqual(expected_num, len(elements))
    for element in elements:
      root = element.tree
      parsed_name = root.getName(is_global_name=False).split(FLATTEN_SEPARATOR)
      self.assertEqual(len(parsed_name), len(set(parsed_name)))
      for name in parsed_name:
        b = any([name in node._name for node in tree.getAllNodes()])
        self.assertTrue(b)
    
  def testFlattenDetached(self):
    """
    Should produce

    root(DUMMY):
      DUMMY__DUMMY1_CHILD
      DUMMY__DUMMY2_CHILD
      DUMMY__DUMMY3_CHILD
      DUMMY__Subparent__DUMMY4_CHILD
    """
    if IGNORE_TEST:
     return
    self.subparent.setIsAttached(False)
    element_list = self.root.flatten()
    flat_tree = element_list[0].tree
    expected_names = [CHILD1, CHILD2, CHILD3, CHILD4]
    names = [l.getName(is_global_name=False) 
             for l in flat_tree.getLeaves()]
    self.assertEqual(set(expected_names[:-1]), set(names))
    name = "%s%s%s" % (self.root._name, FLATTEN_SEPARATOR,
        SUBPARENT)   
    self.assertEqual(name, element_list[1].tree._name)
    child = element_list[1].tree.getChildren()[0]
    self.assertEqual(expected_names[-1], child._name)

  def testFlattenRandomTree(self):
    if IGNORE_TEST:
      return
    tree = NamedTree.createRandomNamedTree(100, 0.5,
        prob_detach=0.2)
    leaves = tree.getLeaves()
    detached_nodes = [n for n in tree.getAllNodes()
                      if not n.isAttached()]
    # Include in the leaves the parents with no attached
    # children
    for node in detached_nodes:
      parent = node.getParent()
      is_leaf = True
      for child in parent.getChildren():
        if child.isAttached():
          is_leaf = False
          break
      if is_leaf and (not parent in leaves):
        leaves.append(parent)
    leaf_full_names = [l._makeFlattenName() for l in leaves]
    elements = tree.flatten()
    names = []
    for e in elements:
      e.tree._checkTreeStructure()
      for leaf in e.tree.getLeaves():
        names.append(leaf._makeFlattenName())
    self.assertEqual(set(leaf_full_names), set(names))

  def testUnflattenOneTree(self):
    if IGNORE_TEST:
      return
    tree_list = self.root.flatten()
    new_tree = NamedTree.unflatten(tree_list)
    self.assertTrue(self.root.isEquivalent(new_tree))

  def testUnflattenTwoTrees(self):
    if IGNORE_TEST:
     return
    self.subparent.setIsAttached(False)
    elements = self.root.flatten()
    new_tree = NamedTree.unflatten(elements)
    self.assertTrue(self.root.isEquivalent(new_tree,
        is_exception=True))

  def testUnflattenManyTrees(self):
    if IGNORE_TEST:
     return
    tree = NamedTree.createRandomNamedTree(100, 0.5,
        prob_detach=0.2)
    tree._checkTreeStructure()
    tree_list = tree.flatten()
    new_tree = NamedTree.unflatten(tree_list)
    self.assertTrue(tree.isEquivalent(new_tree))


if __name__ == '__main__':
  unittest.main()

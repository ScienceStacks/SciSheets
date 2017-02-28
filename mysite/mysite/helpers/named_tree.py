"""
Knows about local and global names for a PositionTree
"""

from mysite.helpers.tree import PositionTree
import random
from collections import namedtuple

ROOT_NAME = ''
GLOBAL_SEPARATOR = "."
FLATTEN_SEPARATOR = "__"
# Describes position of a flattened tree
NamedElement = namedtuple('NamedElement', 'tree position')


class NodeName(object):
  """
  Name for a node in a Tree.
  """

  def __init__(self, node):
    self._node = node

  def get(self, is_global=True):
    """
    Creates a global name
    A name is either relative to a NamedTree or 
    a global name that specifies a path from the root.
    The name does not include the name of the root table and so
    the global name for the root is ''.
    :param bool is_global: return a global name
    :return str:
    """
    if not is_global:
      return self._node._name
    path = self._node.findPathFromRoot()
    del path[0]
    if len(path) > 1:
      result = GLOBAL_SEPARATOR.join(path)
    elif len(path) == 1:
      result = path[0]
    else:
      result = ROOT_NAME
    return result

  def getParsedFlattenedName(self):
    """
    Parses the components of a flattened name.
    :return list-of-str
    """
    parsed_name = self._node._name.split(FLATTEN_SEPARATOR)
    return parsed_name

  @classmethod
  def factory(cls, node, is_global=True):
    return cls(node).get(is_global=is_global)

  @classmethod
  def createFlattenedName(cls, path):
    """
    Creates a flattened name from a path
    :param list-of-str path:
    :return str:
    """
    return FLATTEN_SEPARATOR.join(path)


class NamedTree(PositionTree):
  '''
  A NamedTree knows about names in a PositionTree
  These are paths from the root. 
  '''

  def __init__(self, name):
    super(NamedTree, self).__init__(name)
    self.setName(name)

  @staticmethod
  def pathFromGlobalName(global_name):
    """
    Creates the name path
    :param str global_name:
    :return list:
    """
    return global_name.split(GLOBAL_SEPARATOR)

  def childFromName(self, name, is_relative=True, is_all=False):
    """
    Finds a child with the specified name or None.
    :param name: node name
    :param bool is_relative: relative name (not global)
    :param bool is_all: include the root
    :return PositionTree:
    """
    nodes = self.getChildren(is_recursive=True)
    if is_all:
      nodes.insert(0, self)
    matches = [n for n in nodes 
        if n.getName(is_global_name=(not is_relative))==name]
    if len(matches) == 0:
      child = None
    elif len(matches) == 1:
      child = matches[0]
    else:
      import pdb; pdb.set_trace()
      raise RuntimeError("Found multiple identical names")
    return child

  def copy(self, instance=None):
    """
    :param NamedTree instance:
    :returns object: copy of this object
    """
    # Create an object if one is not provided
    if instance is None:
      instance = NamedTree(self.getName(is_global_name=False))
    super(NamedTree, self).copy(instance=instance)
    return instance

  def isEquivalent(self, other, is_exception=False):
    """
    :param ColumnContainer other:
    :param bool is_exception: generate an AssertionError if false
    :return bool:
    """
    return super(NamedTree, self).isEquivalent(other,
        is_exception=is_exception)

  # TODO: Callers need to set is_relative_name
  def getName(self, is_global_name=True):
    """
    :param bool is_global_name: request a global name
                                if false, node name
    :return str:
    """
    return NodeName.factory(self, is_global=is_global_name)

  def setName(self, name):
    """
    Names must be valid python strings
    :param name: new name
    :return: error string if invalid name, else None
    """
    try:
      _ = compile(name, "string", "eval")
      error = None
      super(NamedTree, self).setName(name)
    except SyntaxError as err:
      error = str(err)
    return error

  def _makeFlattenName(self, flatten_separator=FLATTEN_SEPARATOR,
      is_skip_first=False):
    """
    Creates a flatten name from the root
    :param str flatten_separator:
    :param bool is_skip_first: Don't include the first node
        in the path
    """
    path = self.findPathFromRoot()
    if is_skip_first:
      del path[0]
    name = flatten_separator.join(path)
    return name

  def _detachTrees(self, flatten_separator=FLATTEN_SEPARATOR):
    """
    Construct a set of detached trees with parent names that
    describe the path to the detached tree in the original tree.
    :param str flatten_separator:
    :return list-of-NamedElement: 
    """
    DetachedElement = namedtuple('DetachedElement', 'name position')

    new_tree = self.copy()
    detached = [n for n in new_tree.getAllNodes() if not n.isAttached()]
    elements = [NamedElement(tree=new_tree, position=0)]
    tree_dict = {}  # Values are DetachedElement
    # Acquire information about nodes before the tree is modified
    for node in detached:
      element = DetachedElement(name=node._makeFlattenName(), 
          position=node.getPosition())
      tree_dict[node] = element
    # Cannot change the name until have computed all names
    for node in tree_dict.keys():
      node.setName(tree_dict[node].name)
    # Need a separate pass because all names must be from
    # the original root of the tree
    for node in detached:
      node.removeTree()  # Remove the detached tree
      element = NamedElement(tree=node, position=tree_dict[node].position)
      elements.append(element)
    return elements

  def _flattenAttachedTree(self, flatten_separator=FLATTEN_SEPARATOR,
      is_copy=True):
    """
    Creates a two level tree where the children are leaves and the child name
    is the path from the root to the leaf in the original tree.
    :param str flatten_separator:
    :param bool is_copy: creates a copy of the leaves
                              others, the original tree is modified
    :returns Tree: flattened tree
    """
    cls = type(self)
    new_tree = cls(self.getName(is_global_name=False))
    leaves = []
    for leaf in self.getLeaves():
      new_name = leaf._makeFlattenName(is_skip_first=True)
      if is_copy:
        new_leaf = leaf.copy()
      else:
        new_leaf = leaf
      new_leaf.setName(new_name)
      leaves.append(new_leaf)
    for leaf in leaves:
      leaf.removeTree()
      new_tree.addChild(leaf)
    return new_tree

  def flatten(self, flatten_separator=FLATTEN_SEPARATOR):
    """
    Returns a collection of two level trees (parent, children).
    Each tree in the collection is "detached" in that it can be
    viewed as the root of a separate tree. The two level trees
    have the following properties:
    1. The parents are detached nodes in the original tree.
    2. The name of each parent is a path from the root
       of the original tree to the parent.
    3. The children are leaves in the original Tree. 
    4. The name of a child is a path from the parent (but
       not including the parent) to the child in the original tree.
    5. Concatenating the parent name with one of its children
       creates a path from the root of the original tree to a leaf.
    :param str flatten_separator:
    :return list-of-NamedElement: 
    """
    elements = self._detachTrees()
    new_elements = []
    for element in elements:
      element.tree.validateTree()
      new_tree = element.tree._flattenAttachedTree(is_copy=False)
      new_tree.validateTree()
      named_element = NamedElement(tree=new_tree,
          position=element.position)
      new_elements.append(named_element)
    return new_elements

  @classmethod
  def unflatten(cls, elements, flatten_separator=FLATTEN_SEPARATOR):
    """
    Restores a previously flattened tree to its original structure
    based on the node names.
    :param list-of-NamedElement elements: the first tree in the list becomes
        the root of the unflattened tree
    :param str flatten_separator:
    :return Tree: new tree
    Intermediate nodes are of the same class as the root tree class
    Assumes that detached are constructed so that they are a child
        of the original root of the tree.
    """
    def addChildByFlattenedName(root, flat_child, position=None):
      """
      Adds one child to the tree based on its flattened name.
      The flattened name should not include the root's name.
      :param Tree root: Tree into which child is to be added
      :param Tree flat_child: flattened child node
      :param int/None position:
      :return Tree: node added
      """
      cur_node = root
      tree_cls = type(root)
      name = flat_child.getName(is_global_name=False)
      parsed_name = NodeName(flat_child).getParsedFlattenedName()
      leaf_name = parsed_name[-1]
      # Delete root and leaf
      nonleaf_names = parsed_name[:-1]
      # Create the non-leaves required
      for name in nonleaf_names:
        next_node = [n for n in cur_node.getChildren()
                     if n.getName(is_global_name=False)==name]
        if len(next_node) == 1:
          cur_node = next_node[0]
        elif len(next_node) == 0:
          nonleaf = cur_node.childFromName(name)
          if nonleaf is None:
            nonleaf = tree_cls(name)
            cur_node.addChild(nonleaf)
          cur_node = nonleaf
        else:
          raise RuntimeError("Duplicate name: %s" % name)
      leaf_node = cur_node.childFromName(leaf_name)
      if leaf_node is None:
        leaf_node = flat_child.copy()
        leaf_node.setName(leaf_name)
      cur_node.addChild(leaf_node, position=position)
      return leaf_node

    root = None
    first = True
    for element in elements:
      tree = element.tree
      tree.validateTree()
      tree_cls = type(tree)
      new_tree = tree_cls(tree.getName(is_global_name=False))
      if first:
        # Attached tree
        new_tree.setIsAttached(True)
        root = new_tree
        first = False
      else:
        # Detached tree
        parsed_name = NodeName(tree).getParsedFlattenedName()
        if parsed_name[0] != root.getName(is_global_name=False):
          raise RuntimeError("Invalid name for a detached tree")
        del parsed_name[0]
        new_flattened_name = NodeName.createFlattenedName(parsed_name)
        new_tree.setName(new_flattened_name)
        new_tree = addChildByFlattenedName(root, new_tree, 
            position=element.position)
        new_tree.setIsAttached(False)
        # Get the child path from the root to the parent
      # Do not need to recurse beyond the children since
      # a flattened tree is only two levels.
      for child in tree.getChildren():
        addChildByFlattenedName(new_tree, child)
    return root

  @classmethod
  def createRandomNamedTree(cls, num_nodes, prob_child, seed=0,
      leaf_cls=None, nonleaf_cls=None, prob_detach=0.0):
    """
    Creates a random NamedTree with detached nodes.
    :params int num_nodes: number of nodes in the tree
    :param float prob_child: probability that the next node
                             is a child of the previous
    :param float seed:
    :param Type leaf_cls: type that inherits from Node
    :param Type nonleaf_class: type that inherits from Tree
    :param float prob_detach: probability that a non-leaf is
       detached
    """
    tree = cls.createRandomTree(num_nodes, prob_child, seed=seed,
        leaf_cls=leaf_cls, nonleaf_cls=nonleaf_cls)
    for child in tree.getNonLeaves():
      if random.random() < prob_detach:
        child.setIsAttached(False)
    return tree
        

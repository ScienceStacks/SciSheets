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


class NamedTree(PositionTree):
  '''
  A NamedTree knows about names in a PositionTree
  These are paths from the root. 
  A name is either relative to a NamedTree or 
  a global name that specifies a path from the root.
  The name does not include the name of the root table and so
  the global name for the root is ''.
  A tree may be "attached" or not "attached" to its parent.
  The semantics of not being attached are that the tree is actually
  the root of a separate forest, but it retains the global name structure
  of the original tree.
  '''

  def __init__(self, name):
    super(NamedTree, self).__init__(name)
    self._attached = True  # Flatten semantics keep this as one tree
    self.setName(name)

  def createGlobalName(self, child):
    """
    Creates a global name
    :param PositionTree child:
    :return str:
    """
    path = child.findPathFromRoot()
    del path[0]
    if len(path) > 1:
      result = GLOBAL_SEPARATOR.join(path)
    elif len(path) == 1:
      result = path[0]
    else:
      result = ""  # Root container
    return result

  def createSubstitutedChildrenDict(self, substitution_dict, 
      excludes=None, includes=None, children_dict=None,
      sep=GLOBAL_SEPARATOR):
    """
    Substitutes the nodes in children_dict with the values in the substitution_dict
    :param dict substituion_dict: keys = {nodes, values} are substitutions
    :param list-of-Tree excludes: list of nodes to exclude from list
    :param list-of-Tree includes: list of nodes to include from list
        If None, then include all unless excluded
    :param ChildrenDict children_dict:
    :param str sep: separator in components of global name
    :return recursive dictionary: keys = {name, label, children} 
    """
    if children_dict is None:
      children_dict = self.getChildrenBreadthFirst(excludes=excludes,
          includes=includes)
    name = children_dict["node"].getName()
    name = name.replace('.', sep)
    result = {"name": name,
              "label": children_dict["node"]._name}
    dicts = []
    for this_dict in children_dict["children"]:
      dicts.append(self.createSubstitutedChildrenDict(
          substitution_dict,
          excludes=excludes, 
          includes=includes,
          children_dict=this_dict,
          sep=sep))
    result["children"] = dicts
    return result

  @staticmethod
  def pathFromGlobalName(global_name):
    """
    Creates the name path
    :param str global_name:
    :return list:
    """
    return global_name.split(GLOBAL_SEPARATOR)

  def globalName(self, name, is_relative=True):
    """
    Converts a name relative to the current node to an absolute name. 
    :param str is_relative:
    :param bool is_relative: is a relative name
    :return str: global name
    """
    if not is_relative:
      return name
    current_node_name = self.createGlobalName(self)
    if len(current_node_name) > 0:
      result = GLOBAL_SEPARATOR.join([current_node_name, name])
    else:
      result = name
    return result

  def childFromName(self, name, is_relative=True):
    """
    Finds a child with the specified name or None.
    Note that Columns must be leaves in the Tree.
    :param name: name of the column
    :param bool is_relative: name is relative to the current name
       (as opposed to a global name)
    :return list-of-PositionTree:
    """
    global_name = self.globalName(name, 
        is_relative=is_relative)
    for child in self.getChildren(is_recursive=True):
      global_child_name = self.createGlobalName(child)
      if global_name == global_child_name:
        return child
    return None

  def copy(self, instance=None):
    """
    :param NamedTree instance:
    :returns object: copy of this object
    """
    # Create an object if one is not provided
    if instance is None:
      instance = NamedTree(self.getName(is_global_name=False))
    super(NamedTree, self).copy(instance=instance)
    instance.setIsAttached(self.isAttached())
    return instance

  def isAttached(self):
    if not "_attached" in self.__dict__:
      self._attached = False
    return self._attached

  def isEquivalent(self, other):
    if not (self.isAttached() == other.isAttached()):
      return False
    return super(NamedTree, self).isEquivalent(other)

  def moveChildrenFromOtherTree(self, other):
    """
    Moves children from other to this tree.
    """
    for child in other.getChildren():
      child.removeTree()
      self.addChild(child)

  # TODO: Callers need to set is_relative_name
  def getName(self, is_global_name=True):
    """
    :param bool is_global_name: request a global name
                                if false, node name
    :return str:
    """
    if not is_global_name:
      return super(NamedTree, self).getName()
    parent = self.getParent()
    if parent is None:
      name = ROOT_NAME
    else:
      child = self
      node_name = super(NamedTree, child).getName()
      name = parent.globalName(node_name, is_relative=True)
    return name

  def setIsAttached(self, setting):
    self._attached = setting

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

  def _augmentFlattenedName(self, new_element,
       flatten_separator=FLATTEN_SEPARATOR):
    """
    Adds the name of the new element to the current element
    :param Tree new_element:
    :return str"
    """
    name = "%s%s%s" % (new_element.getName(is_global_name=False), 
        flatten_separator, self.getName(is_global_name=False))
    return name

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
    def addNamePrefix(node, elements, is_prefix_root=False,
         is_prefix_children=False):
      """
      Adds the node's to nodes in trees of the elements
      :param Tree node
      :param list-of-NamedElement elements:
      :param bool is_prefix_root: rename the root of the tree
      :param bool is_prefix_children: rename the children of the tree
      """
      for element in elements:
        if is_prefix_root:
          root_name = element.tree._augmentFlattenedName(node,
              flatten_separator=flatten_separator)
          element.tree.setName(root_name)
        if is_prefix_children:
          for child in element.tree.getChildren():
            child_name = child._augmentFlattenedName(node,
                flatten_separator=flatten_separator)
            child.setName(child_name)

    cls = type(self)
    new_tree = cls(self.getName(is_global_name=False))
    elements = [NamedElement(tree=new_tree, position=0)]
    for child in self.getChildren():
      # Child is a leaf
      if child.isLeaf():
        new_child = child.copy()
        new_tree.addChild(new_child)
      # Non-leaf
      else:
        child_elements = child.flatten(flatten_separator=flatten_separator)
        if child.isAttached():
          # Record the child in the path
          addNamePrefix(child, [child_elements[0]], is_prefix_children=True)
          # Remove the child from the tree
          new_tree.moveChildrenFromOtherTree(child_elements[0].tree)
          elements.extend(list(child_elements[1:]))
        else:
          child._verifyElements(child_elements)
          elements.extend(list(child_elements))
        child._verifyNonleafUnflatten(elements, is_unique=True)
    addNamePrefix(new_tree, elements[1:], is_prefix_root=True)
    new_tree._verifyElements(elements)
    return elements

  def _verifyElements(self, elements):
    """
    Verifies that the leaves of the Tree are the same as
    the number of elements.
    :param list-of-NamedElement elements:
    """
    def leafName(leaf):
      # BUG - WANT PATH FROM self to leaf
      path = leaf.findPathFromRoot()
      return FLATTEN_SEPARATOR.join(path)

    expected_leaves = [leafName(l) for l in self.getLeaves()]
    actual_leaves = []
    for element in elements:
      for leaf in element.tree.getLeaves():
        actual_leaves.append(leafName(leaf))
    if set(expected_leaves) != set(actual_leaves):
      import pdb; pdb.set_trace()
      raise RuntimeError("Failed to find correct number of leaves")

  @staticmethod
  def _elementsString(elements):
    result = ''
    for element in elements:
      result = result + '\n' + '\n' + element.tree.toString()
    return result

  def _verifyNonleafUnflatten(self, elements, is_unique=False):
    """
    Verifies that the child's name appears somewhere in all tree names
    """
    for element in elements:
      for child in element.tree.getChildren():
        full_name = self._augmentFlattenedName(child, 
            flatten_separator=FLATTEN_SEPARATOR)
        name_list = full_name.split(FLATTEN_SEPARATOR)
        if not self.getName(is_global_name=False) in full_name:
          import pdb; pdb.set_trace()
          raise RuntimeError("Invalid path in flattened tree: %s" % full_name)
        if is_unique and len(name_list) < len(set(name_list)):
          import pdb; pdb.set_trace()
          raise RuntimeError("Child name occurs too often: %s" % full_name)

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
      Adds one child to the tree based on its flattened name
      :param Tree root: Tree into which child is to be added
      :param Tree flat_child: flattened child node
      :param int/None position:
      :return Tree: node added
      """
      root._checkTreeStructure()
      cur_node = root
      tree_cls = type(root)
      name = flat_child.getName(is_global_name=False)
      parsed_name = name.split(flatten_separator)
      nonleaf_names = parsed_name[:-1]
      leaf_name = parsed_name[-1]
      for name in nonleaf_names:
        if name == cur_node.getName(is_global_name=False):
          nonleaf = cur_node
        else:
          nonleaf = cur_node.childFromName(name)
          if nonleaf is None:
            nonleaf = tree_cls(name)
            cur_node.addChild(nonleaf)
            cur_node._checkTreeStructure()
          cur_node = nonleaf
      leaf_node = cur_node.childFromName(leaf_name)
      if leaf_node is None:
        leaf_node = child.copy()
        leaf_node.setName(leaf_name)
      cur_node.addChild(leaf_node, position=position)
      return leaf_node

    root = None
    for element in elements:
      tree = element.tree
      tree_cls = type(tree)
      new_tree = tree_cls(tree.getName(is_global_name=False))
      if tree == elements[0].tree:
        # Attached tree
        new_tree.setIsAttached(True)
        root = new_tree
      else:
        # Detached tree
        parsed_name = tree.getName(is_global_name=False).split(flatten_separator)
        if parsed_name[0] != root.getName(is_global_name=False):
          import pdb; pdb.set_trace()
          raise RuntimeError("Invalid name for a detached tree")
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
        

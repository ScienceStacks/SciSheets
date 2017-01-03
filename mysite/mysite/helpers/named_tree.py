"""
Knows about local and global names for a PositionTree
"""

from mysite.helpers.tree import PositionTree
import random

ROOT_NAME = ''
GLOBAL_SEPARATOR = "."
FLATTEN_SEPARATOR = "__"


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

  # TODO: Encode position of the detached child so can reconstruct
  #  the original tree
  def flatten(self, flatten_separator=FLATTEN_SEPARATOR):
    """
    Returns a graph with the leaves as children of the root.
    The names of children are changed to their path name in
    the original graph. Handles "detached" subtrees, which
    are extracted as seperate trees.
    :param str flatten_separator:
    :return list-of-Tree: 
    """
    def makeName(base_name, tree):
      if base_name is None:
        return tree.getName(is_global_name=False)
      return "%s%s%s" % (base_name, flatten_separator, 
          tree.getName(is_global_name=False))

    def setFlattenName(tree_list, base_name):
      """
      Changes the name of trees and their chldren in a list
      :param list-of-Tree tree_list:
      :param str/None base_name:
      """
      if base_name is None:
        return
      for tree in tree_list:
        for child in tree.getChildren():
          child_name = makeName(base_name, child)
          child.setName(child_name)

    cls = type(self)
    new_tree = cls(self.getName(is_global_name=False))
    tree_list = [new_tree]
    for child in self.getChildren():
      # Child is a leaf
      if child.isLeaf():
        new_child = child.copy()
        new_child.setName(makeName(None, new_child))
        new_tree.addChild(new_child)
      # Child is attached. Transfer attached leaves to the new tree
      elif child.isAttached():
        sub_tree_list = child.flatten(flatten_separator=flatten_separator)
        setFlattenName(sub_tree_list, child.getName(is_global_name=False))
        [new_tree.addChild(l) for l in sub_tree_list[0].getChildren()]
        tree_list.extend(sub_tree_list[1:])
      # Child is detached. Add to the list of trees
      else:
        new_child = child.copy()
        new_child.setName(makeName(new_tree.getName(is_global_name=False), child))
        sub_tree_list = new_child.flatten(flatten_separator=flatten_separator)
        setFlattenName(sub_tree_list, None)
        tree_list.extend(sub_tree_list)
    return tree_list

  @classmethod
  def unflatten(cls, trees, flatten_separator=FLATTEN_SEPARATOR):
    """
    Restores a previously flattened tree to its original structure
    based on the node names.
    :param list-of-Trees trees: the first tree in the list becomes
        the root of the unflattened tree
    :param str flatten_separator:
    :return Tree: new tree
    Intermediate nodes are of the same class as the root tree class
    Assumes that detached are constructed so that they are a child
        of the original root of the tree.
    """
    root = None
    for tree in trees:
      tree_cls = type(tree)
      new_tree = tree_cls(tree.getName(is_global_name=False))
      if tree == trees[0]:
        new_tree.setIsAttached(True)
        root = new_tree
      else:
        new_tree.setIsAttached(False)
        parsed_name = new_tree.getName(is_global_name=False).split(flatten_separator)
        if parsed_name[0] != root.getName(is_global_name=False):
          import pdb; pdb.set_trace()
          raise RuntimeError("Invalid name for a detached tree")
        new_tree.setName(parsed_name[1])
        root.addChild(new_tree)
      for child in tree.getChildren():
        parsed_name = child.getName(is_global_name=False).split(flatten_separator)
        cur_node = new_tree
        nonleaf_names = parsed_name[:-1]
        leaf_name = parsed_name[-1]
        for name in nonleaf_names:
          nonleaf = cur_node.childFromName(name)
          if nonleaf is None:
            nonleaf = tree_cls(name)
            cur_node.addChild(nonleaf)
          cur_node = nonleaf
        # cur_node is now the parent of the leaf
        leaf_node = child.copy()
        leaf_node.setName(leaf_name)
        cur_node.addChild(leaf_node)
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
        

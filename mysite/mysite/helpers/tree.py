"""
Implements three classes:
  Node - an element in a tree
  Tree - maintains  and manages the relationships between a 
         Node's parent and its children
  PositionTree - A Tree that tracks the relationship between its
         children (referred to as position). In this implementation,
         the relationship is a linear order.
"""

class Node(object):

  def __init__(self, name):
    self._name = name

  def copy(self, instance=None):
    """
    :param Node instance:
    :return Node:
    """
    if instance is None:
      instance = Node(self._name)
    instance.setName(self._name)
    return instance

  def getAllNodes(self):
    nodes = self.getChildren(is_from_root=True,
                             is_recursive=True)
    nodes.insert(0, self.getRoot())
    return nodes

  def getName(self):
    return self._name

  def isEquivalent(self, node):
    """
    Determines if the node has the same data.
    :return bool: True if equivalent
    """
    return self._name == node._name

  def setName(self, name):
    """
    :param str name:
    """
    self._name = name


class Tree(Node):

  """
  The create, navigate, and transform nodes in a tree structure. 
  Elements of a tree are themselves trees.
  The root is a Tree that has no parent.
  """

  is_always_leaf = False


  def __init__(self, name):
    super(Tree, self).__init__(name)
    self._parent = None
    self._children = []

  def _checkForDuplicateNames(self):
    """
    :return str/None: None if no duplicate
    """
    node_names = [".".join(c.findPathFromRoot())   \
                  for c in self.getAllNodes()]
    if len(node_names) == len(set(node_names)):
      return None
    non_duplicates = []
    for name in node_names:
      if name in non_duplicates:
        return "Duplicate name: %s: " % name
      else:
        non_duplicates.append(name)
    raise RuntimeError("Should have a duplicate")

  def addChild(self, child):
    """
    Adds a tree as a child to this tree.
    Handles moving a subtree from an existing part of the tree.
    :param Tree tree:
    :raises ValueError, RuntimeError:
    """
    if self.isAlwaysLeaf():
      raise RuntimeError("Cannot add child to leaf %s" % self.getName())
    if child in self._children:
      raise ValueError("Duplicate addChild")
    self._children.append(child)
    child.setParent(self)
    if self.validateTree() is not None:
      raise RuntimeError(self.validateTree())

  def copy(self, instance=None):
    """
    :param Tree instance:
    :return Tree:
    """
    # Create an instance if none is provided
    if instance is None:
      instance = Tree(self._name)
    # Copy properties from inherited classes
    instance = super(Tree, self).copy(instance=instance)
    # Set properties for this class
    for child in self.getChildren():
      instance.addChild(child.copy())
    instance.setParent(self.getParent())
    return instance

  def findChildrenWithName(self, name, 
      is_from_root=False, is_recursive=False):
    """
    Find the Tree(s) with the specified name. Note
    that the default values of the options will provide
    the children of the current node.
    :param bool is_from_root: start with the root
    :param bool is_recursive: examine all descendents
    :return list-of-Tree:
    """
    nodes = self.getChildren(is_from_root=is_from_root, 
        is_recursive=is_recursive)
    return [n for n in nodes if n.getName() == name]

  def findPathFromRoot(self):
    """
    A path is a list of member names traversed
    :return list-of-str:
    """
    done = False
    cur = self
    path = []
    while not done:
      path.append(cur._name)
      if cur.getParent() is None:
        done = True
      cur = cur.getParent()
    path.reverse()
    return path

  def getChildren(self, is_from_root=False, is_recursive=False):
    """
    Returns descendent nodes in depth first order.
    :param bool is_from_root: start with the root
    :param bool is_recursive: proceed recursively
    :return list-of-tree:
    """
    if is_from_root:
      start_node = self.getRoot()
    else:
      start_node = self
    if not is_recursive:
      result = start_node._children
    else:
      active_list = list(start_node._children)
      result = []
      while len(active_list) > 0:
        cur = active_list[0]
        if cur in result:
          raise RuntimeError("Tree contains a loop")
        active_list.remove(cur)
        result.append(cur)
        [active_list.insert(0, c) for c in cur._children]
    return result

  def getChildrenNames(self, is_from_root=False, is_recursive=False):
    """
    Returns names in depth first order.
    :param bool is_from_root: start with the root
    :param bool is_recursive: proceed recursively
    :return list-of-tree:
    """
    return [n.getName() for n in self.getChildren(  \
        is_from_root=is_from_root, is_recursive=is_recursive)]

  def getAllNodes(self, is_from_root=False):
    """
    :param bool is_from_root: start with the root
    :return list-of-Tree:
    """
    nodes = self.getChildren(is_from_root=is_from_root,
                                is_recursive=True)  
    if not self in nodes:
      nodes.insert(0, self)
    return nodes

  # TODO: Test with multiple levels of nodes
  def getLeaves(self, is_from_root=False):
    """
    :param bool is_from_root: start with the root
    :return list-of-Tree: nodes without children
    """
    return [n for n in self.getAllNodes(is_from_root=is_from_root)  \
            if len(n.getChildren()) == 0]
    
  # TODO: Test with multiple levels of nodes
  def getNonLeaves(self, is_from_root=False):
    """
    :param bool is_from_root: start with the root
    :return list-of-Tree: nodes without children
    """
    return [n for n in self.getAllNodes(is_from_root=is_from_root)  \
            if len(n.getChildren()) != 0]
    
  def getParent(self):
    return self._parent

  def getRoot(self):
    """
    Returns the root of the trees
    :return Tree:
    """
    if self.getParent() is None:
      return self
    else:
      return self.getParent().getRoot()

  def isAlwaysLeaf(self):
    return self.__class__.is_always_leaf

  def isEquivalent(self, other):
    """
    :return bool: True if equivalent
    """
    is_equivalent = super(Tree, self).isEquivalent(other)
    is_equivalent = is_equivalent and  self.isEquivalentParent(other)
    set1 = set([t.getName() for t in self.getChildren()])
    set2 = set([t.getName() for t in other.getChildren()])
    is_equivalent = is_equivalent and set1 == set2
    if is_equivalent:
      pairs = zip(self.getChildren(), other.getChildren())
      for c1, c2 in pairs:
        is_this = c1.isEquivalent(c2)
        if not is_this:
          import pdb; pdb.set_trace()
        is_equivalent = is_equivalent and is_this
    return is_equivalent

  def isEquivalentParent(self, other):
    """
    :return bool: True if equivalent
    """
    if self.getParent() is None and other.getParent() is None:
      result = True
    elif self.getParent().getName() == other.getParent().getName():
      result = True
    else:
      result = False
    return result
    
  

  def isRoot(self):
    """
    :return bool: True if root
    """
    return self._parent is None

  def removeTree(self):
    """
    Removes the current tree from its parent structure.
    """
    parent = self.getParent()
    if parent is not None:
      parent._children.remove(self)
    self.setParent(None)

  def setParent(self, tree):
    self._parent = tree

  def toString(self, is_from_root=True):
    """
    Create a human readable form of the tree
    :param bool is_from_root: start with the root
    """
    result = ""
    nodes = self.getAllNodes()
    for tree in nodes:
      if tree.getParent() is not None:
        result += "%s->%s\n"  \
            % (tree.getParent().getName(), tree.getName())
    return result
  
  def validateTree(self):
    return self._checkForDuplicateNames()


class PositionTree(Tree):

  """Manages relationships between children."""

  def addChild(self, position_tree, position=None):
    """
    Adds a Tree as a child to the current tree.
    :param PositionTree position_tree:
    :param int position: where to position in list of children
    """
    if position is None:
      position = len(self._children)
    self._children.insert(position, position_tree)
    position_tree.setParent(self)
    error = self.validateTree()
    if error is not None:
      raise RuntimeError(error)

  def copy(self, instance=None):
    """
    :param PositionTree instance:
    :return PositionTree:
    """
    if instance is None:
      instance = PositionTree(self.getName())
    return super(PositionTree, self).copy(instance=instance)

  def getChildAtPosition(self, position):
    """
    :param int position:
    :return PositionTree:
    """
    if position > len(self._children) - 1:
      raise ValueError("Position %d does not exist" % position)
    return self._children[position]

  def getPosition(self):
    """
    Finds the position of this node w.r.t. its parent
    :return int/None:
    """
    if self.getParent() is None:
      return None
    return self.getParent().getPositionOfChild(self)

  def getPositionOfChild(self, child):
    """
    :param PositionTree child:
    :return int/None:
    """
    try:
      return self._children.index(child)
    except ValueError:
      return None

  def isEquivalent(self, other):
    """
    :param PositionTree position_tree:
    """
    is_equivalent = super(PositionTree, self).isEquivalent(other)
    lst1 = [t.getName() for t in self.getAllNodes()]
    lst2 = [t.getName() for t in other.getAllNodes()]
    return is_equivalent and lst1 == lst2
    

  def moveChildToPosition(self, child, position):
    """
    Changes the position of the child with respect to its siblings.
    :param PositionTree child:
    :param int position:
    :raises ValueError: child is not present in Tree
    """
    if not child in self._children:
      raise ValueError("Child %s does not belong to Tree %s"  \
          % (child.getName(), self.getName()))
    self._children.remove(child)
    self._children.insert(position, child)
    if self.validateTree() is not None:
      raise RuntimeError(self.validateTree())

  def toString(self, is_from_root=False):
    """
    Create a human readable form of the tree
    :param bool is_from_root: start with the root
    :return str:
    """
    result = ""
    for tree in self.getAllNodes():
      children = tree.getChildren()
      if len(children) > 0:
        result += "%s\n" % tree.getName()
        pos = 0
        for node in children:
          result += "  %d: ->%s\n"  \
              % (pos, node.getName())
          pos += 1
    return result

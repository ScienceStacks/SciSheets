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

  def getName(self):
    return self._name

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

  def __init__(self, name):
    super(Tree, self).__init__(name)
    self._parent = None
    self._children = []

  def _checkForDuplicateNames(self):
    """
    :return bool: True if no duplicate names
    """
    node_names = [n.getName() for n in self.getDescendents(is_recursive=True, 
        is_from_root=True)]
    return len(node_names) == len(set(node_names))

  def addChild(self, child):
    """
    Adds a tree as a child to this tree.
    Handles moving a subtree from an existing part of the tree.
    :param Tree tree:
    :raises ValueError:
    """
    if child in self._children:
      raise ValueError("Duplicate addChild")
    self._children.append(child)
    self.validate()

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
    nodes = self.getDescendents(is_from_root=is_from_root, 
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
      path.append(cur.getName())
      if cur.getParent() is None:
        done = True
      cur = cur.getParent()
    path.reverse()
    return path
    

  def getParent(self):
    return self._parent

  def getRoot(self):
    """
    Returns the root of the trees
    :return Tree:
    """
    if self._parent is None:
      return self
    else:
      return self._parent.getRoot()

  def getDescendents(self, is_from_root=False, is_recursive=False):
    """
    Returns nodes in depth first order.
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
      active_list = [start_node]
      result = []
      while len(active_list) > 0:
        cur = active_list[0]
        if cur in result:
          raise RuntimeError("Tree contains a loop")
        active_list.remove(cur)
        result.append(cur)
        [active_list.insert(0, c) for c in cur.getChildren()]
    return result
    
  def getLeaves(self, is_from_root=False):
    """
    :param bool is_from_root: start with the root
    :return list-of-Tree: nodes without children
    """
    nodes = self.getDescendents(is_from_root=is_from_root,
                                is_recursive=True)  
    return [n for n in nodes if len(n.getChildren()) == 0]

  def removeTree(self):
    """
    Removes the current tree from its parent structure.
    """
    parent = self.getParent()
    if parent is not None:
      parent._children.remove(tree)
    self._parent = None

  def toString(self, is_from_root=True):
    """
    Create a human readable form of the tree
    :param bool is_from_root: start with the root
    """
    result = ""
    for member in self.getDescendents(is_from_root=is_from_root, 
        is_recursive=True):
      if member.getParent() is not None:
        result += "%s->%s\n"  \
            % (member.getParent().getName(), member.getName())
    return result
  
  def validate(self):
    return self._checkForDuplicateNames()


class PositionTree(Tree):

  """Manages relationships between children."""

  def addChild(self, tree, index=None):
    """
    Adds a Tree as a child to the current tree.
    Handles moving a subtree from an existing part of the tree.
    :param Tree tree:
    :param int index: where to index in list of children
    :raises ValueError: invalid value for index
    """
    if index is None:
      index = len(self._children)
    if index > len(self._children):
      raise ValueError("Position %d > %d, number of children" %
          (index, len(self._children)))
    self._removeTree()
    self._children.insert(index, tree)
    tree._parent = self
    self.validate()

  def getChildAtPosition(self, position):
    """
    :param int position:
    :return PositionTree:
    """
    return self._children[position]

  def getPositionOfChild(self, child):
    """
    :param PositionTree child:
    :return PositionTree/None:
    """
    try:
      return self._children.index(child)
    except ValueError:
      return None

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
    self.validate()

  def toString(self, is_from_root=False):
    """
    Create a human readable form of the tree
    :param bool is_from_root: start with the root
    :return str:
    """
    result = ""
    for tree in self.getDescendents(is_from_root=is_from_root,
        is_recursive=True):
      children = tree.getDescendents(is_from_root=False,
          is_recursive=False):
      if children is not None:
        result += "%s\n" % tree.getName()
        pos = 0
        for node in children:
          result += "  %d: ->%s\n"  \
              % (pos, node.getName())
          pos += 1
    return result

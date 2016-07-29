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
      instance = Node("x")
    instance.setName(self.getName())
    return instance

  def getName(self):
    return self._name

  def isEquivalent(self, node):
    """
    Determines if the node has the same data.
    :return bool: True if equivalent
    """
    return self.getName() == node.getName()

  def setName(self, name):
    """
    :param str name:
    """
    self._name = name

  def migrate(self):
    return self


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
    :return bool: True if no duplicate names
    """
    node_names = [n.getName() for n in self.getChildren(is_recursive=True, 
        is_from_root=True)]
    return len(node_names) == len(set(node_names))

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
    self.validate()

  def copy(self, instance=None):
    """
    :param Tree instance:
    :return Tree:
    """
    if instance is None:
      instance = Tree("x")
    instance = super(Tree, self).copy(instance=instance)
    instance._children = self.getChildren()
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
      path.append(cur.getName())
      if cur.getParent() is None:
        done = True
      cur = cur.getParent()
    path.reverse()
    return path

  def getChildren(self, is_from_root=False, is_recursive=False):
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
    
  def getLeaves(self, is_from_root=False):
    """
    :param bool is_from_root: start with the root
    :return list-of-Tree: nodes without children
    """
    nodes = self.getChildren(is_from_root=is_from_root,
                                is_recursive=True)  
    return [n for n in nodes if len(n.getChildren()) == 0]
    
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

  def isEquivalent(self, tree):
    """
    :return bool: True if equivalent
    """
    is_equivalent = super(Tree, self).isEquivalent(tree)
    is_equivalent = is_equivalent and  \
        self.getParent() == tree.getParent()
    set1 = set([t.getName()  \
        for t in self.getChildren(is_recursive=True)]) 
    set2 = set([t.getName()  \
        for t in tree.getChildren(is_recursive=True)]) 
    is_equivalent = is_equivalent and set1 == set2
    return is_equivalent

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
    for tree in self.getChildren(is_from_root=is_from_root, 
        is_recursive=True):
      if tree.getParent() is not None:
        result += "%s->%s\n"  \
            % (tree.getParent().getName(), tree.getName())
    return result
  
  def validate(self):
    return self._checkForDuplicateNames()


class PositionTree(Tree):

  """Manages relationships between children."""

  def addChild(self, position_tree, position=None):
    """
    Adds a Tree as a child to the current tree.
    Handles moving a subtree from an existing part of the tree.
    :param PositionTree position_tree:
    :param int position: where to position in list of children
    """
    if position is None:
      position = len(self._children)
    position_tree.removeTree()
    self._children.insert(position, position_tree)
    position_tree.setParent(self)
    self.validate()

  def copy(self, instance=None):
    """
    :param PositionTree instance:
    :return PositionTree:
    """
    if instance is None:
      instance = PositionTree("x")
    return super(PositionTree, self).copy(instance=instance)

  def getChildAtPosition(self, position):
    """
    :param int position:
    :return PositionTree:
    """
    if position > len(self._children) - 1:
      raise ValueError("Position %d does not exist" % position)
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

  def isEquivalent(self, position_tree):
    """
    :param PositionTree position_tree:
    """
    is_equivalent = super(PositionTree, self).isEquivalent(position_tree)
    lst1 = [t.getName()  \
        for t in self.getChildren(is_recursive==True)]
    lst2 = [t.getName()  \
        for t in tree.getChildren(is_recursive==True)]
    is_equivalent = is_equivalent and lst1 == lst2
    

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
    for tree in self.getChildren(is_from_root=is_from_root,
        is_recursive=True):
      children = tree.getChildren()
      if children is not None:
        result += "%s\n" % tree.getName()
        pos = 0
        for node in children:
          result += "  %d: ->%s\n"  \
              % (pos, node.getName())
          pos += 1
    return result

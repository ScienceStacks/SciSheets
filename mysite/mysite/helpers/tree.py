"""Implement a tree class in which each element is treated as a tree."""

class Tree(object):

  """
  The expected use case is to inherit from this class.
  Key operations are:
    getParent()
    getChildren()
    getRoot()
    getLeaves()
    findPathToRoot()
    addChild(position_in_children)
    findName(name)

  The root tree is one that has no parent.
  """

  def __init__(self, name):
    self._name = name
    self._parent = None
    self._children = []

  def addChild(self, tree, position=None):
    """
    Adds a tree as a child to this tree.
    :param Tree tree:
    :param int position: where to position in list of children
    :raises ValueError: invalid value for position
    """
    if position is None:
      position = len(self._children)
    if position > len(self._children):
      raise ValueError("Position %d > %d, number of children" %
          (position, len(self._children)))
    self._children.insert(position, tree)
    tree._parent = self

  def removeMember(self):
    """
    Removes the member from the tree, along with it s children.
    """
    parent = self.getParent()
    if parent is None:
      raise ValueError("Attempt to remove the root of the tree.")
    parent._children.remove(self)
    self._parent = None
    

  def getParent(self):
    return self._parent

  def getName(self):
    return self._name

  def getChildren(self):
    return self._children

  def getRoot(self):
    """
    Returns the root of the trees
    :return Tree:
    """
    if self._parent is None:
      return self
    else:
      return self._parent.getRoot()

  def getMembers(self, is_from_root=False):
    """
    Returns all members of the tree in depth first order.
    :param bool is_from_root: start with the root
    :return list-of-tree:
    """
    if is_from_root:
      start_tree = self.getRoot()
    else:
      start_tree = self
    active_list = [start_tree]
    result = []
    while len(active_list) > 0:
      cur = active_list[0]
      active_list.remove(cur)
      result.append(cur)
      [active_list.insert(0, c) for c in cur.getChildren()]
    return result

  def findName(self, name, is_from_root=False):
    """
    FInd the Tree(s) with the specified name
    :param bool is_from_root: start with the root
    :return list-of-Tree:
    """
    members = self.getMembers(is_from_root=is_from_root)  
    return [m for m in members if m.getName() == name]

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
    
  def getLeaves(self, is_from_root=False):
    """
    :param bool is_from_root: start with the root
    :return list-of-Tree: members without children
    """
    members = self.getMembers(is_from_root=is_from_root)  
    return [m for m in members if len(m.getChildren()) == 0]

  def checkForDuplicateNames(self):
    """
    :return bool: True if no duplicate names
    """
    member_names = [m.getName() for m in self.getMembers()]
    return len(member_names) == len(set(member_names))

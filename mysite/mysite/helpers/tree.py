"""
Implements three classes:
  Node - an element in a tree
  Tree - maintains  and manages the relationships between a 
         Node's parent and its children
  TreeIterator - provides depth-first traversal of Trees
  PositionTree - A Tree that tracks the relationship between its
         children (referred to as position). In this implementation,
         the relationship is a linear order.
"""

from statement_accumulator import StatementAccumulator
import random


class Node(object):

  def __init__(self, name):
    self._name = name
    self.setName(name)

  def copy(self, instance=None):
    """
    :param Node instance:
    :return Node:
    """
    if instance is None:
      instance = Node(self._name)
    instance.setName(self._name)
    return instance

  def getName(self):
    return self._name

  def isEquivalent(self, other, is_exception=False):
    """
    :param Node other:
    :param bool is_exception: generate an AssertionError if false
    :return bool:
    """
    msg = None
    if not (self.isAttached() == other.isAttached()):
      msg = "Do not agree on isAttached."
    if self._name != other._name:
      msg = "Do not agree on name."
    if msg is None:
      return True
    if is_exception:
      raise AssertionError(msg)
    else:
      return False

  def setName(self, name):
    """
    :param str name:
    """
    self._name = name


class TreeIterator(object):
  """
  Iterator does a depth first traversal of the associated tree.
  Tree may be a subtree.
  """
  
  def __init__(self, tree):
    """
    :params Tree tree:
    """
    self._current = tree
    self._stop_parent = None
    if tree.getParent() is not None:
      self._stop_parent = tree.getParent()
      
  def _nextSibling(self, node):
    """
    Finds the next sibling of the current node or None
    :param Tree node:
    :return Tree,Tree: sibling, parent
    """
    parent = node.getParent()
    if parent == self._stop_parent:
      return None, None
    if parent is None:
      return None, None
    siblings = parent.getChildren()
    try:
      next_pos = siblings.index(node) + 1
    except Exception as e:
      import pdb; pdb.set_trace()
      raise e.__class__(e.message)
    if (next_pos < len(siblings)) and (next_pos >= 0):
      return siblings[next_pos], parent
    else:
      return None, parent

  def next(self):
    """
    Does a forward depth first traversal of the tree.
    Cases considered are:
      a) current node has a child
      b) current node does not have a child
         i) node has a next sib
         ii) node does not have a next sib
    :return Tree:
    :raises StopIteration: completed traversal
    """
    if self._current is None:
      # No more nodes
      raise StopIteration
    children = self._current._children
    if len(children) > 0:
      # Node has a child
      next = children[0]
    else:
      node = self._current
      while True:
        node, parent = self._nextSibling(node)
        if node is not None:
          # No children, but has a sibling
          next = node
          break
        elif parent is not None:
          node = parent
        else:
          # No sibling and no parent
          next = None
          break
    result = self._current
    self._current = next
    return result


class Tree(Node):

  """
  The create, navigate, and transform nodes in a tree structure. 
  Elements of a tree are themselves trees.
  The root is a Tree that has no parent.
  A Tree is an iterator with both a next and a prev node.
  There is also a way to represent a nested forest, a single
  Tree that embeds other Trees. This is indicated by having
  a node be "attached" or not "attached".
  The semantics of *not* being attached are that the tree is actually
  the root of a separate forest, but it retains the global name structure
  of the original tree.
  """

  is_always_leaf = False


  def __init__(self, name):
    super(Tree, self).__init__(name)
    self._is_attached = True
    self._parent = None
    self._children = []

  def __iter__(self):
    return TreeIterator(self)

  @classmethod
  def findLeavesInNodes(cls, nodes):
    """
    Finds the nodes that have no children within a collection of nodes.
    :param list-of-Tree nodes:
    :return list-of-Tree leaves:
    """
    leaves = []
    node_set = set(nodes)
    for node in nodes:
      children = set(node.getChildren())
      if len(children.intersection(node_set)) == 0:
        leaves.append(node)
    return leaves

  @classmethod
  def findRootsInNodes(cls, nodes):
    """
    Finds the nodes that have no parent within a collection of nodes.
    :param list-of-Tree nodes:
    :return list-of-Tree leaves:
    """
    return [n for n in nodes if 
            (n.getParent() is None) or (not n.getParent() in nodes)]

  # May have a bug with using column as non-leaf class
  @classmethod
  def createRandomTree(cls, num_nodes, prob_child, seed=0,
      leaf_cls=None, nonleaf_cls=None):
    """
    Creates a random tree with the number of nodes specified.
    :params int num_nodes: number of nodes in the tree
    :param float prob_child: probability that the next node
                             is a child of the previous
    :param float seed:
    :param Type leaf_cls: type that inherits from Node
    :param Type nonleaf_class: type that inherits from Tree
    """
    if leaf_cls is None:
      leaf_cls = cls
    if nonleaf_cls is None:
      nonleaf_cls = cls
    count = 0
    def getNodeName(count):
      return "node_%d" % count

    if num_nodes == 0:
      return None
    random.seed(seed)
    root = nonleaf_cls(getNodeName(count))
    parent = root
    if num_nodes == 1:
      return root
    count += 1
    if num_nodes == 2:
      root.addChild(leaf_cls(getNodeName(count)))
      return root
    node = leaf_cls(getNodeName(count))
    parent.addChild(node)
    count = len(root.getAllNodes())
    while  count < num_nodes:
      new_node = leaf_cls(getNodeName(count)) 
      rand = random.random()
      if (rand < prob_child) and (count + 1 < num_nodes):
        if not isinstance(node, nonleaf_cls):
          count += 1
          name = getNodeName(count)
          node = nonleaf_cls(name)
          parent.addChild(node)
        node.addChild(new_node)
      else:
        try:
          parent.addChild(new_node)
        except Exception as e:
          import pdb; pdb.set_trace()
      # Pick a new position to add nodes
      nodes = root.getAllNodes()
      pos = nodes.index(root)
      del nodes[pos]
      idx = random.randint(0, len(nodes)-1)
      node = nodes[idx]
      parent = node.getParent()
      count = len(nodes) + 1
    return root

  def _checkForDuplicateNames(self):
    """
    :raises RuntimeError:
    """
    node_names = [".".join(c.findPathFromRoot())   \
                  for c in self.getAllNodes()]
    if len(node_names) == len(set(node_names)):
      return  # Names are unique
    # Find the duplicate
    non_duplicates = []
    for name in node_names:
      if name in non_duplicates:
        raise RuntimeError("Duplicate name: %s: " % name)
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
    self.validateTree()

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
    instance.setIsAttached(self.isAttached())
    # Set properties for this class
    for child in self.getChildren():
      instance.addChild(child.copy())
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
    return [n._name for n in self.findNodesFromRoot()]

  def findNodesFromAncestor(self, tree):
    """
    Finds the list of nodes from the current node to the tree.
    If tree is not an ancestor, None is returned.
    :param Tree tree;
    :return list-of-Tree or None:
    """
    found = False
    cur = self
    path = []
    while True:
      path.append(cur)
      if cur == tree:
        found = True
        break
      parent = cur.getParent()
      if parent is None:
        break
      cur = parent
    if found:
      path.reverse()
    else:
      path = None
    return path

  def findNodesFromRoot(self):
    """
    Finds the list of nodes from the root.
    :return list-of-Tree:
    """
    return self.findNodesFromAncestor(self.getRoot())

  def getChildren(self, is_from_root=False, is_recursive=False):
    """
    Returns descendent nodes in depth first order.
    :param bool is_from_root: start with the root
    :param bool is_recursive: proceed recursively
    :return list-of-Tree:
    """
    if is_from_root:
      node = self.getRoot()
    else:
      node = self
    if not is_recursive:
      result = node._children
    else:
      result = [n for n in node]
      del result[0]  # Only want the children
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

  def getChildrenBreadthFirst(self, excludes=None, includes=None):
    """
    Returns nodes in a breadth-first dictionary structure starting
    with the current node.
    :param list-of-Tree excludes: list of nodes to exclude from list
    :param list-of-Tree includes: list of nodes to include from list
        If None, then include all unless excluded
    :return ChildrenDict - recursive dictionary structure: 
        keys = {node, children}
    """
    if excludes is None:
      excludes = []
    if includes is None:
      includes = self.getChildren(is_from_root=True,
          is_recursive=True)
      includes.append(self.getRoot())
    result = {}
    if self in excludes:
      return result
    if self in includes:
      result = {"node": self}
    else:
      return result
    result_children = []
    for child in self.getChildren():
      this_result = child.getChildrenBreadthFirst(excludes=excludes, 
          includes=includes)
      if len(this_result.keys()) > 0:
        result_children.append(this_result)
    result["children"] = result_children
    return result

  def getAllNodes(self, is_from_root=False):
    """
    :param bool is_from_root: start with the root
    :return list-of-Tree:
    """
    if is_from_root:
      start_node = self.getRoot()
    else:
      start_node = self
    nodes = []
    for node in start_node:
      if node in nodes:
        import pdb; pdb.set_trace()
        raise RuntimeError("Duplicate occurrence of %s" % node._name)
      nodes.append(node)
    return nodes

  def getAttachedNodes(self, nodes):
    """
    Finds the nodes that are attached to this tree.
    :param list-of-tree nodes:
    :return list-of-Tree: nodes without children
    """
    attached = []
    for node in nodes:
      node_path = node.findNodesFromAncestor(self)
      if node_path is None:
        continue
      node_path.remove(self)
      if all([n.isAttached() for n in node_path]):
        attached.append(node)
    return attached

  # TODO: Test with multiple levels of nodes
  def getLeaves(self, is_from_root=False, is_attached=False):
    """
    :param bool is_from_root: start with the root
    :param bool is_attached: only return leaves attached to the Tree
    :return list-of-Tree: nodes without children
    """
    leaves = [n for n in self.getAllNodes(is_from_root=is_from_root)  \
              if n.isLeaf()]
    if is_attached:
      leaves = self.getAttachedNodes(leaves)
    return leaves
    
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

  def getReverseOrderListOfNodes(self, is_from_root=False):
    if is_from_root:
      start_node = self.getRoot()
    else:
      start_node = self
    nodes = [n for n in start_node]
    nodes.reverse() 
    return nodes

  # TODO: Changed
  def getRoot(self, is_attached=True):
    """
    Returns the root of the trees
    :param bool is_attached: True if want root of attached Tree
    :return Tree:
    """
    if is_attached and not self.isAttached():
      node = self
    elif self.getParent() is None:
      node = self
    else:
      node = self.getParent().getRoot()
    return node

  def getUniqueName(self):
    """
    Returns a unique name for the node
    """
    path = self.findPathFromRoot()
    return '.'.join(path)

  def isAlwaysLeaf(self):
    return self.__class__.is_always_leaf

  def isAttached(self):
    if not "_is_attached" in self.__dict__:
      self._is_attached = False
    return self._is_attached

  def isLeaf(self):
    return len(self.getChildren()) == 0

  def isEquivalent(self, other, is_exception=False):
    """
    :param ColumnContainer other:
    :param bool is_exception: generate an AssertionError if false
    :return bool:
    """
    msg = None
    if not super(Tree, self).isEquivalent(other, 
        is_exception=is_exception):
      msg = "Do not agree on parent of Tree."
    elif not self.isEquivalentParent(other):
      msg = "Do not agree on parent of node."
    else:
      set1 = set([t.getName() for t in self.getChildren()])
      set2 = set([t.getName() for t in other.getChildren()])
      if not set1 == set2:
        msg = "Do not have equivalent children."
      else:
        pairs = zip(self.getChildren(), other.getChildren())
        for c1, c2 in pairs:
          if not c1.isEquivalent(c2, is_exception=is_exception):
            msg = "Do not agree for child named %s" % c1.getName()
    if msg is None:
      return True
    elif is_exception:
      raise AssertionError(msg)
    else:
      return False

  def isEquivalentParent(self, other, is_exception=False):
    """
    :param PositionTree other:
    :param bool is_exeption: determines if an exception is thrown
    :return bool: True if equivalent
    """
    if self.getParent() is None and other.getParent() is None:
      result = True
    elif self.getParent().getName() == other.getParent().getName():
      result = True
    else:
      result = False
    if is_exception:
      raise AssertionError("Parents do not match.")
    return result
    
  def isRoot(self):
    """
    :return bool: True if root
    """
    return self._parent is None

  def moveChildrenFromOtherTree(self, other):
    """
    Moves children from other to this tree.
    """
    for child in other.getChildren():
      child.removeTree()
      self.addChild(child)

  def numDescendents(self):
    """
    :return int: descendents below the current node
    """
    return len(self.getChildren(is_recursive=True))

  def removeTree(self):
    """
    Removes the current tree from its parent structure.
    """
    parent = self.getParent()
    if parent is not None:
      parent._children.remove(self)
    self.setParent(None)

  def setIsAttached(self, setting):
    self._is_attached = setting

  def setParent(self, tree):
    self._parent = tree

  def toString(self, is_from_root=True):
    """
    Create a human readable form of the tree.
    Detached nodes a prefixed by an "*".
    :param bool is_from_root: start with the root
    """
    def nodeString(node):
      if node.isAttached():
        result = node._name
      else:
        result = "[%s]" % node._name
      return result

    sa = StatementAccumulator()
    for node in self.getAllNodes():  # Depth first order
      indent = len(node.findPathFromRoot()) - 1
      sa.indent(indent, is_incremental=False)
      sa.add(nodeString(node))
    return sa.get()

  def _checkTreeStructure(self):
    """
    Verifies that this is a tree.
    """
    nodes_found = []
    pending_nodes = [self.getRoot()]
    while len(pending_nodes) > 0:
      node = pending_nodes[0]
      del pending_nodes[0]
      children = node.getChildren()
      b = all([not c in nodes_found for c in children])
      if not b:
        raise RuntimeError("Multiple paths to a child of %s" %
            node.getName())
      pending_nodes.extend(children)
      nodes_found.extend(children)

  def _checkParentChild(self):
    for child in self._children:
      if child._parent != self:
        import pdb; pdb.set_trace()
        raise RuntimeError("Parent-child mismatch")
      child._checkParentChild()
  
  def validateTree(self):
    self._checkTreeStructure()
    self._checkParentChild()
    self._checkForDuplicateNames()


class PositionTree(Tree):

  """
  Provides access to nodes at specific positions.
  The position of a node is indexed from 0.
  """

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
    self.validateTree()

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

  def isEquivalent(self, other, is_exception):
    """
    :param bool is_exception:
    :param PositionTree position_tree:
    """
    msg = None
    if not super(PositionTree, self).isEquivalent(other,
        is_exception=is_exception):
      msg = "PositionTree do not agree because of ancestor."
    else:
      lst1 = [t.getName() for t in self.getAllNodes()]
      lst2 = [t.getName() for t in other.getAllNodes()]
      if lst1 != lst2:
        msg = "PositionTrees do not agree on positions of children."
    if msg is None:
      return True
    if is_exception:
      raise AssertionError(msg)
    else:
      return False
    
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
    parent = child.getParent()
    child.removeTree()
    parent.addChild(child, position)
    self.validateTree()
    
  def moveChildToOtherchild(self, child, other_child):
    """
    Changes the position in the tree
    :param PositionTree child:
    :param PositionTree other_child:
    :raises ValueError: other_child is a descendent of child,
        which would create a loop in the tree
    """
    if not child.isAlwaysLeaf():
      if other_child in child.getChildren(is_recursive=True):
        raise ValueError("Moving %s to %s creates a loop."  \
            % (child.getName(), other_child.getName()))
    parent = other_child.getParent()
    index = parent.getPositionOfChild(other_child)
    child.removeTree()
    parent.addChild(child, index)
    self.validateTree()

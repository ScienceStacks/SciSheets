"""
Knows about local and global names for a PositionTree
"""

from mysite.helpers.tree import PositionTree

ROOT_NAME = ''
SEPERATOR = "."


class NamedTree(PositionTree):
  '''
  A NamedTree knows about names in a PositionTree
  These are paths from the root. 
  A name is either relative to a NamedTree or 
  a global name that specifies a path from the root.
  The name does not include the name of the root table and so
  the global name for the root is ''.
  '''

  def __init__(self, name):
    super(NamedTree, self).__init__(name)
    self._name = name

  def createGlobalName(self, child):
    """
    Creates a global name
    :param PositionTree child:
    :return str:
    """
    path = child.findPathFromRoot()
    del path[0]
    if len(path) > 1:
      result = SEPERATOR.join(path)
    elif len(path) == 1:
      result = path[0]
    else:
      result = ""  # Root container
    return result

  @staticmethod
  def pathFromGlobalName(global_name):
    """
    Creates the name path
    :param str global_name:
    :return list:
    """
    return global_name.split(SEPERATOR)

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
      result = SEPERATOR.join([current_node_name, name])
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
      if global_child_name.count(SEPERATOR) == 2:
        import pdb; pdb.set_trace()
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
      instance = NamedChild(self.getName())
    super(NamedTree, self).copy(instance=instance)
    return instance

  def isEquivalent(self, other):
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

  def setName(self, name):
    """
    Names must be valid python strings
    :param name: new name
    :return: error string if invalid name, else None
    """
    try:
      _ = compile(name, "string", "eval")
      error = None
      self._name = name
    except SyntaxError as err:
      error = str(err)
    return error

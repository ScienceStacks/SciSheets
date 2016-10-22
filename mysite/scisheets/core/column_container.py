'''
  Implements the ColumnContainer. A ColumnContainer is a PositionTree that has nodes that are
  either Columns or ColumnContainers.
'''

from mysite import settings as settings
from mysite.helpers.versioned_file import VersionedFile
from mysite.helpers.tree import PositionTree
from column import Column
import errors as er
import column as cl


class ColumnContainer(PositionTree):
  '''
  A ColumnContainer can add and delete columns.
  It has no concept of Rows. A ColumnContainer knows about column names, which are paths
  from the root. A name is either relative to a ColumnContainer or 
  a global name that specifies a path from the root ColumnContainer.
  The root ColumnContainer has a VersionedFile that is backing store.
  '''

  def __init__(self, name):
    super(ColumnContainer, self).__init__(name)
    self._name = name
    self._children = []
    self._versioned_file = None

  def columnFromIndex(self, index):
    """
    :return: column object at the index
    """
    return self.getChildAtPosition(index)

  def _createGlobalName(self, child):
    """
    Creates a global name
    :param PositionTree child:
    :return str:
    """
    path = child.findPathFromRoot()
    del path[0]
    if len(path) > 1:
      result = ".".join(path)
    elif len(path) == 1:
      result = path[0]
    else:
      result = ""  # Root container
    return result

  def _relativeNameToGlobalName(self, name, is_relative=True):
    """
    Converts a name relative to the current node to an absolute name. 
    :param str is_relative:
    :param bool is_relative: is a relative name
    :return str: global name
    """
    if not is_relative:
      return name
    current_node_name = self._createGlobalName(self)
    if len(current_node_name) > 0:
      result = ".".join([current_node_name, name])
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
    global_name = self._relativeNameToGlobalName(name, 
        is_relative=is_relative)
    for child in self.getChildren(is_recursive=True):
      global_child_name = self._createGlobalName(child)
      if global_name == global_child_name:
        return child
    return None
        
  def columnFromName(self, name, is_relative=True):
    """
    Finds a column with the specified name or None.
    Note that Columns must be leaves in the Tree.
    :param name: name of the column
    :return: column - column object or None if not found
    """
    leaf = self.childFromName(name, is_relative=is_relative)
    if isinstance(leaf, Column):
      return leaf

  def copy(self, instance=None):
    """
    :param ColumnContainer instance:
    :returns ColumnContainer: copy of this object
    """
    # Create an object if one is not provided
    if instance is None:
      instance = ColumnContainer(self.getName())
    # Set properties specific to this class
    instance.setVersionedFile(self.getVersionedFile())
    instance._children = self.getColumns()
    instance.setName(self.getName())
    return instance

  def getCell(self, row_index, column_index):
    """
    :return: the numpy array of the cells in the column
    """
    child = self.getChildAtPosition(column_index)
    if isinstance(child, Column):
      return child.getCells()[row_index]
    else:
      raise ValueError("Position %d in %s is not a Column" %
          (column_index, self.getName()))

  def getColumnNames(self):
    """
    :return list-of-str:
    """
    return [c.getName() for c in self.getLeaves()]

  def getColumns(self):
    """
    :return: list with the column objects in sequence
    """
    return [c for c in self.getLeaves() if isinstance(c, Column)]

  def getFilepath(self):
    """
    :return str filepath: where table is stored
    """
    if self._versioned_file is None:
      return None
    else:
      return self._versioned_file.getFilepath()

  def getName(self):
    """
    :return: the table name
    """
    return self._name

  def getVersionedFile(self):
    """
    :return VersionedFile/None:
    """
    return self._versioned_file

  def indexFromColumn(self, column):
    """
    Finds the index of the specified column if it is a child
    :param column: column object
    :return int or None:
    """
    return self.getPositionOfChild(column)

  def insertColumn(self, column, index=None):
    """
    Inserts the column after the specified column index
    :param column: object
    :param index: column index
    """
    self.addChild(column, position=index)

  def moveChild(self, child, new_idx):
    """
    Moves the child to after the specified index
    :param PositionTree: what's to be moved
    :param new_idx: new index for column
    """
    self.moveChildToPosition(child, new_idx+1)

  def moveColumn(self, column, new_idx):
    """
    Moves the column to after the specified index
    :param column: column to move
    :param new_idx: new index for column
    """
    self.moveChildToPosition(column, new_idx+1)

  def numColumns(self):
    """
    Returns the number of columns in the table
    """
    return len(self.getColumns())

  def removeChild(self, child):
    """
    Removes the chld object from the table
    """
    child.removeTree()

  def removeColumn(self, column):
    """
    Removes the column object from the table
    """
    self.removeChild(column)

  def setColumns(self, columns):
    [self.addChild(c) for c in columns]

  def setFilepath(self, filepath):
    """
    :param str filepath:
    """
    versioned_file = VersionedFile(
        filepath,
        settings.SCISHEETS_USER_TBLDIR_BACKUP,
        settings.SCISHEETS_MAX_TABLE_VERSIONS)
    self.setVersionedFile(versioned_file)

  def setVersionedFile(self, versioned_file):
    if not self.isRoot():
      raise RuntimeError("Should not set VersionedFile for non-root.")
    self._versioned_file = versioned_file

  def setName(self, name):
    """
    :param name: new table name
    :return: error string if invalid name, else None
    """
    try:
      _ = compile(name, "string", "eval")
      error = None
      self._name = name
    except SyntaxError as err:
      error = str(err)
    return error

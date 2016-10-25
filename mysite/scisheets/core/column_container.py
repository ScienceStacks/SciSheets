'''
  Implements the ColumnContainer. A ColumnContainer is a PositionTree that has nodes that are
  either Columns or ColumnContainers.
'''

from mysite import settings as settings
from mysite.helpers.versioned_file import VersionedFile
from mysite.helpers.named_tree import NamedTree
from column import Column
import errors as er
import column as cl


class ColumnContainer(NamedTree):
  '''
  A ColumnContainer can add and delete columns.
  It has no concept of Rows. 
  A ColumnContainer knows about column names, which are paths
  from the root. A name is either relative to a ColumnContainer or 
  a global name that specifies a path from the root ColumnContainer.
  The name does not include the name of the root table and so
  the global name for the root table is ''.
  The root ColumnContainer has a VersionedFile that is backing store.
  '''

  def __init__(self, name):
    super(ColumnContainer, self).__init__(name)
    self._name = name
    self._versioned_file = None

  def columnFromIndex(self, index):
    """
    :return: column object at the index
    """
    return self.getChildAtPosition(index)
        
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
    super(ColumnContainer, self).copy(instance=instance)
    # Set properties specific to this class
    if self.getVersionedFile() is not None:
      instance.setVersionedFile(self.getVersionedFile())
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
    return [c.getName() for c in self.getLeaves()  \
            if isinstance(c, Column)]

  def getColumns(self, is_recursive=True):
    """
    :param bool is_recursive: finds all columns from current node
    :return: list with the column objects in sequence
    """
    if is_recursive:
      candidates = self.getLeaves()
    else:
      candidates = self.getChildren()
    return [c for c in candidates if isinstance(c, Column)]

  def getFilepath(self):
    """
    :return str filepath: where table is stored
    """
    if self._versioned_file is None:
      return None
    else:
      return self._versioned_file.getFilepath()

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

  def isEquivalent(self, other):
    return super(ColumnContainer, self). isEquivalent(other)

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

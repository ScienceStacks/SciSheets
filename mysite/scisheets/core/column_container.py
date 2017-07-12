'''
  Implements the ColumnContainer. A ColumnContainer is a PositionTree that has nodes that are
  either Columns or ColumnContainers.
'''

from mysite import settings as settings
from common_versioned_file.versioned_file import VersionedFile
from common_tree.named_tree import NamedTree
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
    self.setName(name)
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
    :raises ValueError: name not found
    """
    leaf = self.childFromName(name, is_relative=is_relative)
    if ColumnContainer.isColumn(leaf):
      return leaf
    else:
      raise ValueError("Column is not a leaf.")

  def copy(self, instance=None):
    """
    :param ColumnContainer instance:
    :returns ColumnContainer: copy of this object
    """
    # Create an object if one is not provided
    if instance is None:
      instance = ColumnContainer(self.getName(is_global_name=False))
    super(ColumnContainer, self).copy(instance=instance)
    # Set properties specific to this class
    if self.getVersionedFile() is not None:
      instance.setVersionedFile(self.getVersionedFile())
    instance.setName(self.getName(is_global_name=False))
    return instance

  def getCell(self, row_index, column_id):
    """
    :param int row_index:
    :param int/str column_id: either the column index or its name
    :return: the numpy array of the cells in the column
    """
    if isinstance(column_id, int):
      child = self.getChildAtPosition(column_id)
    else:
      child = self.childFromName(column_id, is_relative=False)
    if ColumnContainer.isColumn(child):
      return child.getCells()[row_index]
    else:
      raise ValueError("Position %d in %s is not a Column" %
          (column_index, self.getName()))

  def getColumnNames(self):
    """
    :return list-of-str:
    """
    return [c.getName() for c in self.getLeaves()  \
            if ColumnContainer.isColumn(c)]

  def getColumns(self, is_recursive=True, is_attached=True):
    """
    :param bool is_recursive: finds all columns from current node
    :param bool is_attached: only return attached columns
    :return: list with the column objects in sequence
    """
    if is_recursive:
      candidates = self.getLeaves()
    else:
      candidates = self.getChildren()
    if is_attached:
      candidates = self.getAttachedNodes(candidates)
    return [c for c in candidates if ColumnContainer.isColumn(c)]

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

  @classmethod
  def isColumn(cls, child):
    """
    :param NamedTree child:
    :return bool: True if is a Column
    """
    return isinstance(child, Column)

  def isEquivalent(self, other, is_exception=False):
    """
    :param ColumnContainer other:
    :param bool is_exception: generate an AssertionError if false
    :return bool:
    """
    return super(ColumnContainer, self). isEquivalent(other,
        is_exception=is_exception)

  def moveChild(self, child, new_idx):
    """
    Moves the child to after the specified index
    :param PositionTree: what's to be moved
    :param new_idx: new index for column
    """
    self.moveChildToPosition(child, new_idx+1)

  def moveColumn(self, column, new_column_id):
    """
    Moves the column to after the specified index
    :param NamedTree column: column to move
    :param new_idx: new index for column
    """
    self.moveChildToPosition(column, new_idx+1)

  def numColumns(self):
    """
    Returns the number of columns in the table
    """
    return len(self.getColumns())

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
    if self.isRoot():
      self._versioned_file = versioned_file
    else:
      self._versioned_file = None

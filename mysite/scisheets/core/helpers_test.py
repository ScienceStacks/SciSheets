'''
   Utilities used for testing MVCSheets code.
'''

from mysite.helpers.versioned_file import VersionedFile
from scisheets.ui.dt_table import DTTable
import column as cl
import contextlib
import numpy as np
import os
import pickle
import StringIO
import sys


TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                       'test_dir')
TEST_TABLE = "TEST_TABLE"
TEST_FILENAME = "%s.pcl" % TEST_TABLE
TABLE_FILEPATH = os.path.join(TEST_DIR, TEST_FILENAME)
MAX_VERSIONS = 3

# Constants
COLUMN = "DUMMY_COLUMN"
COLUMN1 = "DUMMY1_COLUMN"
COLUMN2 = "DUMMY2_COLUMN"
COLUMN3 = "DUMMY3_COLUMN"
COLUMN4 = "DUMMY4_COLUMN"
COLUMN5 = "DUMMY5_COLUMN"
COLUMN2_INDEX = 1
TABLE_NAME = "DUMMY_TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
FORMULA = "A+B"
COLUMN1_CELLS = ["one", "two", "three"]
COLUMN2_CELLS = [10.1, 20.0, 30.0]
COLUMN5_CELLS = [100.0, 200.0, 300.0]

def toList(val):
  """
  Converts a value to a list.
  :param val: value to convert
  :return: list
  """
  if isinstance(val, list):
    data_list = val
  elif isinstance(val, np.ndarray):
    data_list = val.tolist()
  else:
    data_list = [val]
  return data_list

def compareValues(val1, val2):
  """
  Compares two scalars or lists
  :param val1: first value to compare
  :param val2: secondvalue to compare
  :return: Boolean
  """
  list1 = toList(val1)
  list2 = toList(val2)
  if len(list1) != len(list2):
    return False
  is_equal = True
  for idx in range(len(list1)):
    is_equal = is_equal and (list1[idx] == list2[idx])
  return is_equal

def createColumn(name, data=np.array([]), table=None, formula=None):
  """
  :param name: str column name
  :param data: np.ndarray data values
  :param table: Table that reerences the column
  :param formula: formula in column
  :return: column object with data populated
  """
  aColumn = cl.Column(name)
  aColumn.addCells(data)
  aColumn.setTable(table)
  aColumn.setFormula(formula)
  return aColumn

def createTable(name, column_name=None):
  """
  :param str name: str table name
  :param str or list column_name: column(s) to create
  :return: Table object
  """
  if column_name is None:
    colnms = []
  elif isinstance(column_name, list):
    colnms = column_name
  else:
    colnms = [column_name]
  table = DTTable(name)
  versioned_file = VersionedFile(TABLE_FILEPATH, TEST_DIR, MAX_VERSIONS)
  table.setVersionedFile(versioned_file)
  for colnm in colnms:
    column = cl.Column(colnm)
    column.addCells(range(5), replace=True)
    table.addColumn(column)
  pickle.dump(table, open(TABLE_FILEPATH, "wb"))
  return table

def compareTableData(table1, table2, excludes=None):
  """
  Compares the data in the tables.
  :param Table table1, table2:
  :param list-of-int excludes: column indicies excluded from the comparison
  :return bool: True if comparison matches
  """
  if excludes is None:
    excludes = []
  if table1.numColumns() != table2.numColumns():
    return False
  for idx in range(table1.numColumns()):
    if not idx in excludes:
      data1 = table1._columns[idx].getCells()
      data2 = table2._columns[idx].getCells()
      if data1 != data2:
        return False
  return True

@contextlib.contextmanager
def stdoutIO(stdout=None):
  """
  Captures standard output when executing a python command
  :param stdout: where standard output is directed
  """
  # Captures standard output
  # Usage: with stdoutIO() as s:
  old = sys.stdout
  if stdout is None:
    stdout = StringIO.StringIO()
  sys.stdout = stdout
  yield stdout
  sys.stdout = old

def augmentPythonPath(thisFile):
  """
  Ensures that the python path includes the directory of the
  test file
  :param str thisFile: path to the file being tested.
  """
  if not isinstance(thisFile, list):
    filelist = [thisFile]
  else:
    filelist = thisFile
  for aFile in filelist:
    sys.path.append(os.path.dirname(aFile))

def setupTableInitialization(o):
  """
  Adds a table to the unittest object.
  """
  o.table = createTable(TABLE_NAME)
  column1 = cl.Column(COLUMN1)
  column1.addCells(COLUMN1_CELLS)
  o.table.addColumn(column1)
  column2 = cl.Column(COLUMN2)
  column2.addCells(COLUMN2_CELLS)
  o.table.addColumn(column2)
  column5 = cl.Column(COLUMN5)
  column5.addCells(COLUMN5_CELLS)
  o.table.addColumn(column5)


class TableFileHelper(object):
  """
  Creates and removes a dummy Table File
  """

  @classmethod
  def doesTableFileExist(cls, table_filename, filedir, suffix="pcl"):
    """
    Checks if the table file exists
    :param table_filename: table file name without extension
    :param table_filedir: directory for the table file
    :param suffix: suffix for filename
    :return: boolean
    """
    full_filename = "%s.%s" % (table_filename, suffix)
    full_path = os.path.join(filedir, full_filename)
    return os.path.exists(full_path)

  def __init__(self, table_filename, table_filedir, table_name=None):
    """
    :param table_filename: name of the dummy table file
    :param table_filedir: directory for the table file
    """
    self.table = None
    self._table_filename = table_filename
    self._table_filedir = table_filedir
    self._full_path = os.path.join(table_filedir,
        "%s.pcl" % self._table_filename)
    self._table_name = table_name
    if self._table_name is None:
      self._table_name = table_filename

  def create(self):
    """
    Creates Table file and the table
    """
    if os.path.exists(self._full_path):
      fh = open(self._full_path, "rb")
      self.table = pickle.load(fh)
      fh.close()
    else:
      self.table = DTTable(self._table_name)
      pickle.dump(self.table, open(self._full_path, "wb"))
    versioned_file = VersionedFile(TABLE_FILEPATH, 
        TEST_DIR, MAX_VERSIONS)
    self.table.setVersionedFile(versioned_file)

  def destroy(self):
    """
    Destroys a Table file
    """
    if TableFileHelper.doesTableFileExist(self._table_filename,
        self._table_filedir):
      os.remove(self._full_path)



'''Evaluates formulas in a Table.'''

import pickle
import numpy as np
import collections

################### Classes ############################
# Used to define a DataClass
# cls is the data type that can be tested in isinstance
# cons is a function that constructs an instance of cls
#   taking as an argument a list
# Usage: data_class = DataClass(cls=np.ndarray, 
#                               cons=(lambda(x: np.array(x))))
DataClass = collections.namedtuple('DataClass', 'cls cons')

########### CONSTANTS ################
def makeArray(aList):
  return np.array(aList)
DATACLASS_ARRAY = DataClass(cls=np.ndarray,
    cons=makeArray)


################### Functions #########################

def executeStatements(statements):
  """
  Executes one or more statements contained in a string
  :param statements: string or list of str  of one or more python statements
  :return: str error from the execution or None
  """
  if isinstance(statements, list):
    statements = '\n'.join(statements)
  elif isinstance(statements, str):
    statements = statements
  else:
    raise ValueError("Must be a str or list.")
  # pylint: disable=W0122
  try:
    #exec(statements, globals(), locals())
    exec(statements, globals())
    error = None
  # pylint: disable=W0703
  except Exception as err:
    # Report the error without changing the table
    error = str(err)
  return error

def assignColumnValuesFromVariable(column, prefix=""):
  """
  Creates an assignment statement that assigns the data values
  of a column to its column name.
  :param column: Column object
  :param prefix: string prepended to column name to form variable
  """
  variable_name = "%s%s" % (prefix, column.getName())
  values = globals()[variable_name]
  if isinstance(values, list):
    list_values = values
  elif "tolist" in dir(values):
    list_values = values.tolist()
  else:
    list_values = list(values)
  column.addCells(list_values, replace=True)
  data_class = column.getDataClass()
  values = data_class.cons(column.getCells())
  globals()[variable_name] = values

def assignVariableFromColumnValues(column, prefix=""):
  """
  Creates an assignment statement that assigns the data values
  of a column to its column name.
  :param column: Column object
    :param str prefix: string prepended to the column name
  """
  variable_name = "%s%s" % (prefix, column.getName())
  statement = "global %s" % variable_name  # Make this global
  executeStatements(statement)
  data_class = column.getDataClass()
  values = data_class.cons(column.getCells())
  globals()[variable_name] = values

def getTableFromFile(file_path):
  """
  Get the table from the file
  :param str table_file: full path to table file
  """
  fh = open(file_path, "rb")
  table = pickle.load(fh)
  fh.close()
  return table


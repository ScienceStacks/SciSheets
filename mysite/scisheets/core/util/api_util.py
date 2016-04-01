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
def getTableFromFile(file_path, verify=True):
  """
  Get the table from the file
  :param str table_file: full path to table file
  :param bool verify: checks the file path in the table
  :raises ValueError: Checks that the file path is set
  """
  fh = open(file_path, "rb")
  try:
    table = pickle.load(fh)  # BUG - fails here
  except Exception as e:
    import pdb; pdb.set_trace()
  fh.close()
  if verify and table.getFilepath() != file_path:
    raise ValueError("File path is not set")
  return table

def writeTableToFile(table):
  """
  Get the table from the file
  :param Table table:
  """
  pickle.dump(table, open(table.getFilepath(), "wb"))


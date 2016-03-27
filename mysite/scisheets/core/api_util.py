'''Evaluates formulas in a Table.'''

import pickle


def executeStatement(statement):
  """
  Executes one or more statements contained in a string
  :param statement: string or list of str  of one or more python statements
  :return: str error from the execution or None
  """
  if isinstance(statement, list):
    statements = '\n'.join(statement)
  elif isinstance(statement, str):
    statements = statement
  else:
    raise ValueError("Must be a str or list.")
  # pylint: disable=W0122
  try:
    #exec(statement, globals(), locals())
    exec(statement, globals())
    error = None
  # pylint: disable=W0703
  except Exception as err:
    # Report the error without changing the table
    error = str(err)
  return error

def makeAssignmentStatement(column):
  """
  Creates an assignment statement that assigns the data values
  of a column to its column name.
  :param column: Column object
  :return: str statement
  """
  name = column.getName()
  values = str(column.getCells())
  statement = "%s = %s(%s)" % (
      column.getName(),
      column.getDataClass(),
      values)
  return statement

def getTableFromFile(file_path):
  """
  Get the table from the file
  :param str table_file: full path to table file
  """
  fh = open(table_file, "rb")
  return pickle.load(fh)


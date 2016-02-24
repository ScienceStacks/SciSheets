'''
   Exceptions used in MVCSheets
'''

class Error(Exception):
  """
  Base error class
  """
  pass

class NotYetImplemented(Error):
  """
  Code not yet written
  """
  pass

class DataTypeError(Error):
  """
  Mismatch for Column data types
  """
  pass

class ColumnNotFound(Error):
  """
  Referenced column does not exist
  """
  pass

class DuplicateColumnName(Error):
  """
  Two columns with the same name
  """
  pass

class NoNameRow(Error):
  """
  Lack the referenced row
  """
  pass

class InternalError(Error):
  """
  Fails a consistency test
  """
  pass


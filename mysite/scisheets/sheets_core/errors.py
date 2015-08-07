'''
   Exceptions used in MVCSheets
'''

class Error(Exception):
  pass

class NotYetImplemented(Error):
  pass

class DataTypeError(Error):
  pass

class ColumnNotFound(Error):
  pass

class DuplicateColumnName(Error):
  pass

class NoNameRow(Error):
  pass

class InternalError(Error):
  pass


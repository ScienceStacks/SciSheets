'''
   Helpers for accessing data tables.
'''

from scisheets.models import UploadedFiles
from Database.db_access import DBAccess
from CommonUtil.util import ConvertType, ConvertTypes
from mysite import settings
import sqlite3
import os

#############################
# Exceptions
#############################
class Error(Exception):
  """Base class for exceptions."""

class DBError(Error):
  def __init__(self, msg):
    self.msg = msg

class TypeError(Error):
  def __init__(self, msg):
    self.msg = msg


#############################
# Constants
#############################
_DEFAULT_DB = settings.DATABASES['default']['NAME']


#############################
# Functions
#############################a
def SQLType(value):
  # Returns: string for the correct SQL type of the value
  if type(value) == str:
    return 'TEXT'
  if type(value) == float:
    return 'REAL'
  if type(value) == int:
    return 'INTEGER'
  raise TypeError("Invalid type %g" % value)


#############################
# Classes
#############################
class FileTable(object):
  # Base class for creating a table from a file
  # The database table is managed outside of Django since Django cannot
  # handle dynamic creation and deletion of tables. However, there is
  # a Django model, UploadedFiles, that tracks the uploaded files present.
  # This is called the FileTable.

  @classmethod
  def RemoveUploadedFile(cls, filename, db=_DEFAULT_DB):
    # Removes an uploaded file from UPLOADED_FILE_TABLE
    # Input: filename - name of file to remove
    #        db - database to use
    dba = DBAccess(db_path=db)
    sql_str = "DELETE FROM %s WHERE table_name='%s'" % (
        settings.UPLOAD_FILE_TABLE, filename)
    dba.ExecuteQuery(sql_str, commit=True)

  @classmethod
  def DataTableList(cls, db=_DEFAULT_DB):
    # Output: List of data tables
    dba = DBAccess(db)
    sql_str = "SELECT table_name FROM %s" % settings.UPLOAD_FILE_TABLE
    rows, _ = dba.ExecuteQuery(sql_str)
    table_list = [r[0] for r in rows]
    return table_list

  def __init__(self, file_path, db=_DEFAULT_DB):
    # file_path - path to the file to process
    # db - path to the database file
    self._file_path = file_path
    self._upload_dir, self._raw_filename = os.path.split(file_path)
    self._db_path = db
    try:
      pos = self._raw_filename.index('.')
    except:
      raise FileError("Invalid file name %s" % self._raw_filename)
    self._filename = self._raw_filename[0:pos]
    self._table_name = self._filename
    self._conn = None
    self._cursor = None
    self._GetColumnNames()

  def _GetColumnNames(self):
    self._colnames = None
    f = open(self._file_path, 'r')
    line = f.readline()
    f.close()
    self._colnames = line.split()

  def _AddFileToTable(self):
    # Records the file in the Django UploadedFiles table
    dba = DBAccess(db_path=self._db_path)
    if not dba.IsTablePresent(settings.UPLOAD_FILE_TABLE):
      raise DBError('%s does not exist' % settings.UPLOAD_FILE_TABLE)
    sql_str = "SELECT * from %s where table_name='%s'" % (
      settings.UPLOAD_FILE_TABLE, self._filename)
    rows, _ = dba.ExecuteQuery(sql_str)
    if len(rows) == 0:
      sql_str = '''
           INSERT into %s ('file_name', 'file_path', 'table_name')
           VALUES ('%s', '%s', '%s')
           ''' % (settings.UPLOAD_FILE_TABLE,
                  self._filename, 
                  self._file_path, 
                  self._table_name)
      dba.ExecuteQuery(sql_str, commit=True)

  def _RemoveFileFromTable(self):
    row = UploadedFiles.objects.filter(file_name=self._filename)
    row.delete()

  def _ConstructSQLTableCreate(self, values):
    dba = DBAccess()
    if dba.IsTablePresent(self._table_name):
      return ''
    sql_str = "CREATE TABLE %s (" % self._table_name
    for n in range(len(self._colnames)):
      sql_str += "%s %s" % (self._colnames[n], SQLType(values[n]))
      if n+1 >= len(self._colnames):
        sql_str += ")"
      else:
        sql_str += ","
    return sql_str

  def _ConstructSQLTableInsert(self, values):
    sql_str = "INSERT INTO %s VALUES(" % self._table_name
    for n in range(len(values)):
      sql_str += "'%s'" % values[n]
      if n < len(values) - 1:
        sql_str += ","
      else:
        sql_str += ")"
    return sql_str

  def _ExecuteSQL(self, sql_str='', CloseDB=False):
    if self._conn is None:
      self._conn = sqlite3.connect(self._db_path)
      self._cursor = self._conn.cursor()
    if len(sql_str) > 0:
      self._cursor.execute(sql_str)
    if CloseDB:
      self._conn.commit()
      self._conn.close()
      self._conn = None
      self._cursor = None

  def CreateAndPopulateTable(self):
    self._AddFileToTable()
    n = 0
    IsTableCreated = False
    with open(self._file_path, 'r') as f:
      while True:
        line = f.readline()
        if len(line) == 0:
          break
        n += 1
        if n == 1:  # skip the first line
          continue
        values = ConvertTypes(line.split())
        if not IsTableCreated:
          sql_str = self._ConstructSQLTableCreate(values)
          if len(sql_str) > 0:
            self._ExecuteSQL(sql_str=sql_str)
          IsTableCreated = True
        sql_str = self._ConstructSQLTableInsert(values)
        self._ExecuteSQL(sql_str=sql_str)
    self._ExecuteSQL(CloseDB=True)

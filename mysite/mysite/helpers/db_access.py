'''
   Helpers that virtualize the underlying database used.
'''

from mysite import settings
import sqlite3
import os

#############################
# Exceptions
#############################
class Error(Exception):
  """Base class for exceptions."""

class FileError(Error):
  def __init__(self, msg):
    self.msg = msg

class DBError(Error):
  def __init__(self, msg):
    self.msg = msg


#############################
# Constants
#############################
CUR_DB = settings.DATABASES['default']['NAME']


#############################
# Classes
#############################
class DBAccess(object):
  "Abstraction for the underlying database"

  def __init__(self, db_path=CUR_DB):
    self._db_path = db_path

  def ExecuteQuery(self, sql_str, conn=None, 
      cursor=None, close_conn=True, commit=False):
    # Input: conn: database connection
    #        sql_str: sql command to execute
    #        conn: connection to use, if any
    #        close_conn: flag indicating if connection is to be closed
    #        commit: flag indicating if a commit should be done
    #          assumes that updates/inserts have commit=True
    # Output: rows, cursor - results of the query, cursor
    if conn is None:
      conn = sqlite3.connect(self._db_path)
    if cursor is None:
      cursor = conn.cursor()
    s = cursor.execute(sql_str)
    if commit:
      conn.commit()
      result = None
    else:
      result = s.fetchall()
    if close_conn:
      conn.close()
      conn = None
      cursor = None
    return result, cursor

  def IsTablePresent(self, table_name):
    # Input: table - string name of talbe
    # Output: True if present; otherwise false
    sql_str = "SELECT name FROM sqlite_master "
    sql_str += "WHERE type='table' AND name='%s'" % table_name
    query_result, _ = self.ExecuteQuery(sql_str)
    return len(query_result) > 0

  def GetSchema(self, table_name):
    # Input: table_name  - string name of the table
    # Output: List of field names
    sql_str = "select * from %s where 1=0" % table_name
    _, cursor = self.ExecuteQuery(sql_str, close_conn=False)
    field_names = [r[0] for r in cursor.description]
    return field_names

  # BUG: NEED TESTS
  def GetSchemaFromSelect(self, select_statement):
    # Input: select_statement - select statement
    # Output: List of field names
    DUMMY_VIEW = "DBAccessXXYYZZ"
    sql_str = "create view %s as %s" % (DUMMY_VIEW, select_statement)
    self.ExecuteQuery(sql_str)
    result = self.GetSchema(DUMMY_VIEW)
    sql_str = "drop view %s" % DUMMY_VIEW
    self.ExecuteQuery(sql_str)
    return result
    

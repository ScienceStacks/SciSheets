'''Code used commonly in tests'''
from mysite import settings
import os
import shutil
import sqlite3

def ComputeDBPaths():
  # Output: real_db_path, test_db_path
  real_db_path = settings.DATABASES.get('default').get('NAME')
  real_db_path_list = os.path.split(real_db_path)
  real_db_name = real_db_path_list[1]
  test_db_name = "test_%s" % real_db_name
  test_db_path = os.path.join(real_db_path_list[0], test_db_name)
  return real_db_path, test_db_path

REAL_DB_PATH, TEST_DB_PATH = ComputeDBPaths()
FILE_NAME = 'test_file_to_db'
RAW_FILE_NAME = FILE_NAME + '.tsv'
INITIAL_PATH = os.path.join(settings.BASE_DIR, 'mysite/helpers')
FILE_PATH = os.path.join(INITIAL_PATH, RAW_FILE_NAME)
TEST_TABLE = 'TESTXXX'

def ExecuteSQL(conn, sql_str, cursor=None):
  result = ''
  if cursor is None:
    cursor = conn.cursor()
  if len(sql_str) > 0:
    cursor.execute(sql_str)
    result = cursor.fetchall()
  return result

def SetupTestDB():
  # Verifiy the setup of the test database: (a) contains the real database,
  # (b) accesible from sqlite
  # Test that we have the tables from the real DB
  # Returns: True if setup successful; else, false
  shutil.copyfile(REAL_DB_PATH, TEST_DB_PATH)
  # Test the set up
  conn = sqlite3.connect(TEST_DB_PATH)
  sql_str = '''SELECT name FROM sqlite_master 
               WHERE type='table' AND name='%s' ''' % 'heatmap_uploadedfiles'
  if len(ExecuteSQL(conn, sql_str)) != 1:
    return False
  # Verfity can create and access a test table
  cursor = conn.cursor()
  sql_str = "CREATE TABLE %s (c1 text, c2 real)" % TEST_TABLE
  ExecuteSQL(conn, sql_str, cursor=cursor)
  sql_str = "INSERT INTO %s values ('a', 3.2)" % TEST_TABLE
  ExecuteSQL(conn, sql_str, cursor=cursor)
  sql_str = "INSERT INTO %s values ('b', 4.2)" % TEST_TABLE
  ExecuteSQL(conn, sql_str, cursor=cursor)
  conn.commit()
  sql_str = "select * from %s" % TEST_TABLE
  rows = ExecuteSQL(conn, sql_str, cursor=cursor)
  conn.close()
  return len(rows) == 2

def TearDownTestDB():
  if os.path.isfile(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

def CreateTableWithData(tablename, conn):
  # Input - tablename: name of the table to create
  #         conn: database connection
  col1 = "name"
  col2 = "address"
  sql_str = "create table %s (%s TEXT, %s REAL);\n" % (tablename, col1, col2)
  sql_str += "insert into %s (%s, %s) values ('Jer', 33);" % (
      tablename, col1, col2)
  conn.executescript(sql_str)

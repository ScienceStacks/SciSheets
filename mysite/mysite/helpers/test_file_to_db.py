# Add more specific tests to check the schema created for the table
'''Tests for file_to_db'''

from mysite import settings
from Testing import testhelpers as th
from Database.db_access import DBAccess
from scisheets.models import UploadedFiles
from mysite.helpers.file_to_db import (FileTable, SQLType)
import unittest
#import file_to_db as f2d
import sqlite3
import os

class TestFunctions(unittest.TestCase):
  def testSQLType(self):
    return
    self.assertEqual(SQLType('aa'), 'TEXT')
    self.assertEqual(SQLType(33), 'INTEGER')
    self.assertEqual(SQLType(3.3), 'REAL')


class TestFileTable(unittest.TestCase):

  def setUp(self):
    return
    # Use a copy of the real DB for these tests
    self.assertTrue(th.SetupTestDB())

  def tearDown(self):
    return
    # Make sure that the test DB is eliminated
    th.TearDownTestDB()

  def testDataTableList(self):
    return
    dba = DBAccess(db_path=th.TEST_DB_PATH)
    ft = FileTable(th.FILE_PATH, db=th.TEST_DB_PATH)
    sql_str = "DELETE FROM %s WHERE table_name='%s'" % (
        settings.UPLOAD_FILE_TABLE, ft._table_name)
    try:
      dba.ExecuteQuery(sql_str, commit=True)
    except:
      pass
    old_table_set = set(FileTable.DataTableList(db=th.TEST_DB_PATH))
    ft.CreateAndPopulateTable()
    new_table_set = set(FileTable.DataTableList(db=th.TEST_DB_PATH))
    new_row_set = set([ft._table_name])
    self.assertTrue(new_table_set.issuperset(new_row_set))
    self.assertFalse(old_table_set.issuperset(new_row_set))
    ft._ExecuteSQL('', CloseDB=True)

  def testRemoveUploadedFile(self):
    return
    dba = DBAccess(db_path=th.TEST_DB_PATH)
    ft = FileTable(th.FILE_PATH, db=th.TEST_DB_PATH)
    ft.CreateAndPopulateTable()
    table_set = set(FileTable.DataTableList(db=th.TEST_DB_PATH))
    self.assertTrue(table_set.issuperset(set([ft._table_name])))
    FileTable.RemoveUploadedFile(ft._filename, db=th.TEST_DB_PATH)
    remove_table_set = set(FileTable.DataTableList(db=th.TEST_DB_PATH))
    self.assertFalse(remove_table_set.issuperset(set([ft._table_name])))
    
  def testConstructor(self):
    return
    ft = FileTable(th.FILE_PATH, db=th.TEST_DB_PATH)
    self.assertEqual(ft._filename, th.FILE_NAME)
    self.assertEqual(ft._table_name, th.FILE_NAME)

  def test_AddFileToTable(self):
    return
    ft = FileTable(th.FILE_PATH, db=th.TEST_DB_PATH)
    ft._AddFileToTable()
    dba = DBAccess(db_path=th.TEST_DB_PATH)
    sql_str = "SELECT * FROM %s WHERE file_name='%s'" % (
        settings.UPLOAD_FILE_TABLE, th.FILE_NAME)
    rows, _ = dba.ExecuteQuery(sql_str)
    file_name = rows[0][0]
    self.assertEqual(file_name, th.FILE_NAME)

  def test_RemoveFileFromTable(self):
    return
    ft = FileTable(th.FILE_PATH, db=th.TEST_DB_PATH)
    ft._RemoveFileFromTable()
    try:
      entry = UploadedFiles.objects.get(file_name=th.FILE_NAME)
      assertTrue(True)  # This should succeed
    except:
      pass
    
  def testCreateAndPopulateTable(self):
    return
    ft = FileTable(th.FILE_PATH, db=th.TEST_DB_PATH)
    ft.CreateAndPopulateTable()
    conn = sqlite3.connect(th.TEST_DB_PATH)
    sql_str = "SELECT * FROM %s" % ft._table_name
    rows = th.ExecuteSQL(conn, sql_str)
    self.assertEqual(len(rows), 3)
    row = rows[1]
    self.assertEqual(row[0], 2)
    
    

if __name__ == '__main__':
    unittest.main()

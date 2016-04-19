from mysite import settings
from mysite.helpers.db_access import DBAccess
from mysite.helpers import testhelpers as th
import unittest
import file_to_db as f2d
import os
import sqlite3


##########################
# Tests
##########################
class TestDBAccess(unittest.TestCase):

  def setUp(self):
    return
    # Use a copy of the real DB for these tests
    self.assertTrue(th.SetupTestDB())
    self.db_path = th.TEST_DB_PATH
    self.dba = DBAccess(db_path=self.db_path)
    self.conn = sqlite3.connect(self.db_path)
    self.cursor = self.conn.cursor()

  def tearDown(self):
    return
    # Make sure that the test DB is eliminated
    if self.conn is not None:
      self.conn.close()
    th.TearDownTestDB()

  def testExecuteQuery(self):
    return
    sql_str = "SELECT * FROM sqlite_master"
    rows, _ = self.dba.ExecuteQuery(sql_str)
    rows1, _ = self.dba.ExecuteQuery(sql_str, conn=self.conn, close_conn=False)
    self.assertEqual(rows, rows1)
    rows2, ret_cursor = self.dba.ExecuteQuery(sql_str, conn=self.conn, 
        cursor=self.cursor, close_conn=False)
    self.assertEqual(rows, rows2)
    self.assertEqual(ret_cursor, self.cursor)

  def testIsTablePresent(self):
    return
    TABLE_NAME = "testGetSchema"
    th.CreateTableWithData(TABLE_NAME, self.conn)
    b = self.dba.IsTablePresent(TABLE_NAME)
    self.assertTrue(b)
    b = self.dba.IsTablePresent('dummy_dummy')
    self.assertFalse(b)

  def testGetSchema(self):
    return
    TABLE_NAME = "testGetSchema"
    th.CreateTableWithData(TABLE_NAME, self.conn)
    schema = self.dba.GetSchema(TABLE_NAME)
    for col in ['name', 'address']:
      try:
        col in schema
        b = True
      except:
        b = False
      self.assertTrue(b, "Couldn't find column %s" % col)


if __name__ == '__main__':
    unittest.main()

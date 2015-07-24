'''Tests for helpers_views'''

from mysite import settings
from mysite.helpers.db_access import DBAccess
from mysite.helpers import testhelpers as th
from heatmap.helpers.table_view import (TableForm, QueryForm)
from heatmap.helpers import test_helpers_views as thv
from django.test import TestCase  # Provides mocks for client interactions
import os
import sqlite3

class TestTableViews(TestCase):

  def setUp(self):
    self.assertTrue(th.SetupTestDB())
    self.db_path = th.TEST_DB_PATH
    self.dba = DBAccess(db_path=self.db_path)
    self.conn = sqlite3.connect(self.db_path)
    self.cursor = self.conn.cursor()

  def tearDown(self):
    th.TearDownTestDB()

  def testmaketable(self):
    CLIENT_URL = '/heatmap/maketable/'
    TABLE_LIST = ['data_rev', 'data']
    response = self.client.get(CLIENT_URL)
    self.assertEqual(response.status_code, 200)
    form_data = {'numrows': 10, 'lastrow': 1}
    form = TableForm(data=form_data)
    post_dict = {'display_form': form,
                 'tablename': TABLE_LIST[0],
                 'table_list': TABLE_LIST}
    response = self.client.post(CLIENT_URL, post_dict)
    self.assertEqual(response.status_code, 200)

  def testDeletetable(self):
    # Put in the file to delete
    CLIENT_URL = '/heatmap/upload/'
    post_dict = {'filename': thv.TEST_DATA_FILENAME}
    response = self.client.post(CLIENT_URL, post_dict)
    # Delete the file
    CLIENT_URL = '/heatmap/deletetable/'
    response = self.client.get(CLIENT_URL)
    self.assertEqual(response.status_code, 200)
    post_dict = {'tablename': thv.TEST_DATA_TABLENAME}
    response = self.client.post(CLIENT_URL, post_dict)
    self.assertEqual(response.status_code, 200)

  def testQuery(self):
    CLIENT_URL = '/heatmap/query/'
    TABLE_LIST = ['data_rev', 'data']
    TABLE_NAME = "testQuery"
    response = self.client.get(CLIENT_URL)
    self.assertEqual(response.status_code, 200)
    # Test the post
    th.CreateTableWithData(TABLE_NAME, self.conn)
    query_string = "SELECT * from %s" % TABLE_NAME
    form = QueryForm(data={'query_string': query_string})
    post_dict = {'form': form,
                 'table_list': TABLE_LIST}
    response = self.client.post(CLIENT_URL, post_dict)
    self.assertEqual(response.status_code, 200)
      


if __name__ == '__main__':
    unittest.main()

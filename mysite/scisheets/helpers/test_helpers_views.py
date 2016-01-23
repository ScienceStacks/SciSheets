'''Tests for helpers_views'''

from mysite import settings
from django.test import TestCase  # Provides mocks for client interactions
import os

def ComputeDBPaths():
  # Output: real_db_path, test_db_path
  real_db_path = settings.DATABASES.get('default').get('NAME')
  real_db_path_list = os.path.split(real_db_path)
  real_db_name = real_db_path_list[1]
  test_db_name = "test_%s" % real_db_name
  test_db_path = os.path.join(real_db_path_list[0], test_db_name)
  return real_db_path, test_db_path

TEST_FILE_UPLOAD_PATH = 'mysite/uploads'
TEST_DATA_TABLENAME = 'test_helpers_views_data'
TEST_DATA_FILENAME = TEST_DATA_TABLENAME + ".tsv"

class TestHelpers(TestCase):

  def _TestContext(self, context, kvdict):
    # Tests for the presence of all the keys
    # and their associated values
    # Input: context - a Django view context
    #        kv_dict - dictionary where key is in context
    #                  and the value of that key is the value in kv_dict
    for k,v in kvdict.items():
      self.assertTrue(k in context, "Key %s is not present" % k)
      self.assertEqual(v, context[k], 
          "Value %s is not present for key %s" % (str(v), k))

  def testLetter(self):
    response = self.client.get('/letter/')
    self.assertEqual(response.status_code, 200)
    self._TestContext(response.context, {'person_name': 'John'})

  def testPlot(self):
    CLIENT_URL = '/plot/' + TEST_DATA_FILENAME + '/'
    response = self.client.get(CLIENT_URL)
    self.assertEqual(response.status_code, 200)
    self.assertTrue('xlabel' in response.context)
    self.assertEqual(response.context['xlabel'], 'Time')
    test_dict = {'xlabel': 'Time',
                 'ylabel': 'Day',
                }
    self._TestContext(response.context, test_dict)

  def testUpload(self):
    CLIENT_URL = '/upload/'
    response = self.client.get(CLIENT_URL)
    self.assertEqual(response.status_code, 200)
    post_dict = {'filename': TEST_DATA_FILENAME}
    response = self.client.post(CLIENT_URL, post_dict)
    self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

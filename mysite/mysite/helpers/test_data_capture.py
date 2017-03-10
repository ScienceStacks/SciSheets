'''Tests for DataCapture'''

from mysite import settings
import unittest
from mysite.helpers.data_capture import DataCapture
import os

TEST_FILE = 'data_capture_file'


class TestFunctions(unittest.TestCase):

  def setUp(self):
    self.capture = DataCapture(TEST_FILE)
  
  def testSetAndGet(self):
    a = range(10)
    b = range(20)
    self.capture.setData([a,b])
    x, y = self.capture.getData()
    self.assertTrue(a == x)
    self.assertTrue(b == y)
    

if __name__ == '__main__':
    unittest.main()

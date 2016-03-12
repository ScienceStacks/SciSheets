'''Tests for column'''

import numpy as np
from util import isNumber
import unittest

class TestUtil(unittest.TestCase):

  def setUp(self):
    pass

  def testIsNumber(self):
    self.assertTrue(isNumber(4))
    self.assertTrue(isNumber(range(4)))
    self.assertTrue(isNumber([3, 4, None]))
    self.assertFalse(isNumber([3, 4, None, 'a']))
    self.assertFalse(isNumber([3, 4, np.nan, 'a']))
    self.assertTrue(isNumber([3, 4, np.nan, 0]))


if __name__ == '__main__':
  unittest.main()

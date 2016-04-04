'''
Tests for API Utilities. These are codes shared with other
files in core.
 '''

from ...core import helpers_test as ht
import api_util
import numpy as np
import os
import unittest

ARRAY_INT = np.array(range(4))
ARRAY_INT_LONG = np.array(range(5))
ARRAY_FLOAT = [0.01*x for x in range(4)]


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestAPIUtil(unittest.TestCase):

  def testCompareIterables(self):
    self.assertFalse(api_util.compareIterables(ARRAY_INT, ARRAY_INT_LONG))
    self.assertFalse(api_util.compareIterables(ARRAY_INT,
        np.array([0.1*n for n in range(4)])))
    self.assertTrue(api_util.compareIterables(ARRAY_INT, ARRAY_INT))
    self.assertTrue(api_util.compareIterables(ARRAY_FLOAT, ARRAY_FLOAT))


if __name__ == '__main__':
  unittest.main()

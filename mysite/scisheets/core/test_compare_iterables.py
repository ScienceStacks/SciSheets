'''Tests for compare_iterables'''

from compare_iterables import compareIterables
import unittest
import numpy as np

ARRAY_INT = np.array(range(4))
ARRAY_INT_LONG = np.array(range(5))
ARRAY_FLOAT = [0.01*x for x in range(4)]

#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestColumn(unittest.TestCase):

  def testAll(self):
    self.assertFalse(compareIterables(ARRAY_INT, ARRAY_INT_LONG))
    self.assertFalse(compareIterables(ARRAY_INT,
        np.array([0.1*n for n in range(4)])))
    self.assertTrue(compareIterables(ARRAY_INT, ARRAY_INT))
    self.assertTrue(compareIterables(ARRAY_FLOAT, ARRAY_FLOAT))


if __name__ == '__main__':
  unittest.main()

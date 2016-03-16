'''Tests for column'''

import numpy as np
from util import isNumbers, isFloats, findDatatypeForValues
import unittest

class TestUtil(unittest.TestCase):

  def setUp(self):
    pass
  
  def testfindDatatypeForValues(self):
    self.assertEqual(findDatatypeForValues(['a', 'bb']),
                    '|S1000')
    self.assertEqual(findDatatypeForValues([1.0, 2.0]),
                    np.float64)
    self.assertEqual(findDatatypeForValues([1.0, 2.0, np.nan]),
                    np.float64)
    self.assertEqual(findDatatypeForValues([1, 2]),
                    np.int)
    self.assertEqual(findDatatypeForValues([False, True]),
                    np.bool)
    self.assertEqual(findDatatypeForValues([1, 2, 'a']),
                    '|S1000')
    self.assertEqual(findDatatypeForValues([1, 2, None]),
                    object)

  def testIsNumbers(self):
    self.assertTrue(isNumbers(4))
    self.assertTrue(isNumbers(range(4)))
    self.assertTrue(isNumbers([3, 4, None]))
    self.assertFalse(isNumbers([3, 4, None, 'a']))
    self.assertFalse(isNumbers([3, 4, np.nan, 'a']))
    self.assertTrue(isNumbers([3, 4, np.nan, 0]))

  def testIsFloat(self):
    self.assertTrue(isFloats(4.0))
    self.assertTrue(isFloats([4.0, 3.0]))
    self.assertTrue(isFloats([4.0, np.nan, 3.0]))
    self.assertFalse(isFloats(range(4)))
    self.assertFalse(isFloats([3, 4, None]))
    self.assertFalse(isFloats([3, 4, None, 'a']))
    self.assertFalse(isFloats([3, 4, np.nan, 'a']))
    self.assertTrue(isFloats([3, 4, np.nan, 0]))


if __name__ == '__main__':
  unittest.main()

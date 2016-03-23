'''Tests for column'''

import numpy as np
from util import isFloats, \
    DTYPE_STRING, getType, coerceData
import util
import unittest


# pylint: disable=C0111
# pylint: disable=E1101
class TestUtil(unittest.TestCase):

  def setUp(self):
    pass

  def testIsFloat(self):
    self.assertTrue(isFloats(4.0))
    self.assertTrue(isFloats([4.0, 3.0]))
    self.assertTrue(isFloats([4.0, np.nan, 3.0]))
    self.assertFalse(isFloats(range(4)))
    self.assertFalse(isFloats([3, 4, None]))
    self.assertFalse(isFloats([3, 4, None, 'a']))
    self.assertFalse(isFloats([3, 4, np.nan, 'a']))
    self.assertTrue(isFloats([3, 4, np.nan, 0]))

  def testGetType(self):
    self.assertEqual(getType('aa'), str)
    self.assertEqual(getType('1.0'), util.XFloat)
    self.assertEqual(getType(1.0), util.XFloat)
    self.assertEqual(getType('2'), util.XInt)
    self.assertEqual(getType(2), util.XInt)
    self.assertEqual(getType(1), util.XBool)
    self.assertEqual(getType(None), None)
    self.assertEqual(getType(np.nan), util.XFloat)
    self.assertEqual(getType('True'), util.XBool)
    self.assertEqual(getType(True), util.XBool)
    self.assertEqual(getType((1,2)), object)

  def _CoerceData(self, values, expected_type):
    """
    Tests combinations of values with other types
    :param list values: what's being tested
    :param expected_type: a type
    """
    array = np.array(coerceData(values))
    self.assertEqual(array.dtype, expected_type)
    values.append('a String')
    array = np.array(coerceData(values))
    self.assertTrue(str(array.dtype)[1]=='S')
    values.append(None)
    array = np.array(coerceData(values))
    self.assertEqual(array.dtype, object)

  def testCoerceData(self):
    self._CoerceData([1.0, 1], np.float64)
    self._CoerceData([1, 2], np.int64)
    self._CoerceData([True, False], np.bool)
    self._CoerceData([True, False, 3], np.int64)
    array = np.array(coerceData([1.0, 1, None]))
    self.assertEqual(array.dtype, np.float64)



if __name__ == '__main__':
  unittest.main()

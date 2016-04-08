'''Tests for column'''

import numpy as np
import cell_types
import unittest


# pylint: disable=C0111
# pylint: disable=E1101
class TestUtil(unittest.TestCase):

  def setUp(self):
    pass

  def testIsFloat(self):
    self.assertTrue(cell_types.isFloats(4.0))
    self.assertTrue(cell_types.isFloats([4.0, 3.0]))
    self.assertTrue(cell_types.isFloats([4.0, np.nan, 3.0]))
    self.assertFalse(cell_types.isFloats(range(4)))
    self.assertFalse(cell_types.isFloats([3, 4, None]))
    self.assertFalse(cell_types.isFloats([3, 4, None, 'a']))
    self.assertFalse(cell_types.isFloats([3, 4, np.nan, 'a']))
    self.assertTrue(cell_types.isFloats([3, 4, np.nan, 0]))

  def testGetType(self):
    self.assertEqual(cell_types.getType('aa'), str)
    self.assertEqual(cell_types.getType('1.0'), cell_types.XFloat)
    self.assertEqual(cell_types.getType(1.0), cell_types.XInt)
    self.assertEqual(cell_types.getType('2'), cell_types.XInt)
    self.assertEqual(cell_types.getType(2), cell_types.XInt)
    self.assertEqual(cell_types.getType(1), cell_types.XBool)
    self.assertEqual(cell_types.getType(None), None)
    self.assertEqual(cell_types.getType(np.nan), cell_types.XFloat)
    self.assertEqual(cell_types.getType('True'), cell_types.XBool)
    self.assertEqual(cell_types.getType(True), cell_types.XBool)
    self.assertEqual(cell_types.getType((1,2)), object)

  def _CoerceData(self, values, expected_type):
    """
    Tests combinations of values with other types
    :param list values: what's being tested
    :param expected_type: a type
    """
    array = np.array(cell_types.coerceData(values))
    self.assertEqual(array.dtype, expected_type)
    values.append('a String')
    array = np.array(cell_types.coerceData(values))
    self.assertTrue(str(array.dtype)[1]=='S')
    values.append(None)
    array = np.array(cell_types.coerceData(values))
    self.assertEqual(array.dtype, object)

  def testCoerceData(self):
    self._CoerceData([1.0, 1], np.int64)
    self._CoerceData([1, 2], np.int64)
    self._CoerceData([True, False], np.bool)
    self._CoerceData([True, False, 3], np.int64)
    array = np.array(cell_types.coerceData([1.0, 1, None]))
    self.assertEqual(array.dtype, np.float64)

  def testCoerceString(self):
    values = ['..', None, None]
    coerced_values = cell_types.coerceData(values)
    array = np.array(coerced_values)
    self.assertFalse(isinstance(values, np.float64))
    self.assertFalse(isinstance(values, np.int64))



if __name__ == '__main__':
  unittest.main()

'''Tests for cell_types.'''

from extended_array import ExtendedArray
import numpy as np
import cell_types
import unittest


# pylint: disable=C0111
# pylint: disable=E1101
class TestUtil(unittest.TestCase):

  def setUp(self):
    pass

  def testIsFloat(self):
    self.assertTrue(cell_types.isFloat(4.1))
    self.assertTrue(cell_types.isFloat(u'4.1'))
    self.assertFalse(cell_types.isFloat(4.0))
    self.assertTrue(cell_types.isFloat(np.nan))
    self.assertFalse(cell_types.isFloat('an'))
    self.assertFalse(cell_types.isFloat(1))

  def testIsStr(self):
    self.assertTrue(cell_types.isStr('a'))
    self.assertTrue(cell_types.isStr(u'a'))
    self.assertTrue(cell_types.isStr(u'1'))
    self.assertFalse(cell_types.isStr(1))

  def testIsFloats(self):
    self.assertTrue(cell_types.isFloats(4.1))
    self.assertFalse(cell_types.isFloats(4.0))
    self.assertTrue(cell_types.isFloats([4.1, 3.0]))
    self.assertTrue(cell_types.isFloats([4.1, np.nan, 3.0]))
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
    array = np.array(cell_types.coerceData([ 1, 2, '[1, 2]']))
    self.assertTrue(str(array.dtype)[1]=='S')
    array = np.array(cell_types.coerceData([ 'aa', 'bb', '[1, 2]']))
    self.assertTrue(str(array.dtype)[1]=='S')
    array = np.array(cell_types.coerceData([ 1.1, 2, '[1, 2]']))
    self.assertTrue(str(array.dtype)[1]=='S')

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

  def testIterableType(self):
    self.assertEqual(cell_types.getIterableType([u'empty cell']),
      unicode)
    self.assertEqual(cell_types.getIterableType([1,2]), 
      cell_types.XInt)
    self.assertEqual(cell_types.getIterableType([1.1, 2]),
      cell_types.XFloat)
    self.assertEqual(cell_types.getIterableType([True, False]),
      cell_types.XBool)
    self.assertEqual(cell_types.getIterableType([[1,2], [3]]), object)

  def testIsEquivalentFloats(self):
    self.assertFalse(cell_types.isEquivalentFloats(1, 2))
    self.assertTrue(cell_types.isEquivalentFloats(1.0, 1.0))
    self.assertFalse(cell_types.isEquivalentFloats(1.0, 2.0))
    self.assertTrue(cell_types.isEquivalentFloats(1, 1))
    self.assertFalse(cell_types.isEquivalentFloats(1, 1.0001))
    self.assertFalse(cell_types.isEquivalentFloats(1, np.nan))
    self.assertTrue(cell_types.isEquivalentFloats(np.nan, np.nan))

  def testIsEquivalentData(self):
    self.assertTrue(cell_types.isEquivalentData(1, 1))
    self.assertFalse(cell_types.isEquivalentData(1, 2))
    range1 = range(5)
    range2 = range(6)
    self.assertTrue(cell_types.isEquivalentData(range1, range1))
    self.assertFalse(cell_types.isEquivalentData(range1, range2))
    values1 = [np.nan, np.nan, np.nan]
    values2 = ExtendedArray(0.41509)
    self.assertFalse(cell_types.isEquivalentData(values1, values2))

  def testIsEquivalentData(self):
    self.assertTrue(cell_types.isEquivalentData(1, 1))
    self.assertFalse(cell_types.isEquivalentData(1, 2))
    range1 = range(5)
    range2 = range(6)
    self.assertTrue(cell_types.isEquivalentData(range1, range1))
    self.assertFalse(cell_types.isEquivalentData(range1, range2))
    values1 = [np.nan, np.nan, np.nan]
    values2 = ExtendedArray(0.41509)
    self.assertFalse(cell_types.isEquivalentData(values1, values2))

  def testIsEquivalentData2(self):
    values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13',
       '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
       '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
       '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46',
       '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57',
       '58', '59', '60', '61', '62', '63', '64']
    array = ExtendedArray(values)
    self.assertTrue(cell_types.isEquivalentData(array, array))

  def testIsEquivalentNestedArray(self):
    array = ExtendedArray([np.array([ 0.069]), 
                          np.array([ 0.015,  0.069,  0.021]), 
                          np.array([ 0.027]),
                          np.array([ 0.027]), np.array([ 0.027])])
    self.assertTrue(cell_types.isEquivalentData(array, array))
    array2 = ExtendedArray([np.array([ 0.069]), 
                          np.array([ 0.15,  0.069,  0.021]),  # 0.015->0.15
                          np.array([ 0.027]),
                          np.array([ 0.027]), np.array([ 0.027])])
    self.assertFalse(cell_types.isEquivalentData(array, array2))

  def testIsEquivalentMismatchedData(self):
    values1 = ExtendedArray([[0.0], [1.0], [2.0], [3.0], None, None])
    values2 = [[0.0], [1.0], [2.0], [3.0]]
    values3 = [[u'0'], [u'1'], [u'2'], [u'3']]
    self.assertTrue(cell_types.isEquivalentData(values1, values3))
    self.assertTrue(cell_types.isEquivalentData(values1, values2))

  def testIsEquivalentMismatchedData(self):
    values1 = ExtendedArray([ 0.04123,  0.00729,  0.03847,  0.01675,  0.01031,  0.01563,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan,      np.nan,      np.nan,
            np.nan,      np.nan,      np.nan,      np.nan])
    values2 = [0.04123, 0.00729, 0.03847, 0.01675, 0.01031, 0.01563, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    self.assertTrue(cell_types.isEquivalentData(values1, values2))

  def testIsEquivalentNestedNan(self):
    values1 = ExtendedArray([np.array([ 1.]), np.array([ 0.183,  0.966,  0.966]), np.array([ np.nan]),  \
       np.array([ np.nan]), np.array([ np.nan]), None, None])
    values2 = np.array([np.array([ 1.]), np.array([ 0.183,  0.966,  0.966]), np.array([ np.nan]),  \
       np.array([ np.nan])])
    self.assertTrue(cell_types.isEquivalentData(values1, values2))

  def testIsEquivalentUnicode(self):
    values1 = ExtendedArray([  0.,   1.,   2.,   3.,
        np.nan,  np.nan,  np.nan])
    values2 = [u'0.0', u'1.0', u'2.0', u'3.0', None]
    self.assertTrue(cell_types.isEquivalentData(values1, values2))

  def testIsStrs(self):
    vals = ['a', 'b']
    self.assertTrue(cell_types.isStrs(vals))
    vals = [1, 'b']
    vals = np.array(['a', 'b'])
    self.assertTrue(cell_types.isStrs(vals))


if  __name__ == '__main__':
  unittest.main()

'''Tests for ExtendedArray.'''

import numpy as np
from extended_array import ExtendedArray
import unittest


# pylint: disable=C0111
# pylint: disable=E1101
class TestExtendedArray(unittest.TestCase):

  def testBasic(self):
    name = 'dummy'
    values = range(100)
    ea = ExtendedArray(name=name, values=values)
    self.assertEqual(ea.name, name)
    ea_values = [x for x in ea]
    self.assertEqual(ea_values, values)

  def testType(self):
    name = 'dummy'
    values = range(100)
    ea = ExtendedArray(name=name, values=values)
    self.assertEqual(ea.dtype, np.int64)
    values = [x*0.1 for x in range(100)]
    ea = ExtendedArray(name=name, values=values)
    self.assertEqual(ea.dtype, np.float64)

  def testSetName(self):
    name = 'dummy'
    values = range(100)
    ea = ExtendedArray(name=name, values=values)
    self.assertEqual(ea.name, name)
    name = 'another dummy'
    ea.setName(name)
    self.assertEqual(ea.name, name)

  def testLen(self):
    values = range(5)
    ea = ExtendedArray(name='Dummy', values=values)
    self.assertEqual(len(values), len(ea))
    ea = ExtendedArray(name='Dummy', values=1)
    self.assertEqual(1, len(ea))

  def testSingleValue(self):
    ea = ExtendedArray(name='Dummy', values=1)
    self.assertEqual(len(ea), 1)


if __name__ == '__main__':
  unittest.main()

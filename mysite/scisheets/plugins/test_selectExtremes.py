""" Tests for selectExtremes """

from scisheets.plugins.selectExtremes import selectExtremes
import unittest
import numpy as np

RANGE = range(4)
DOUBLE_RANGE = range(2*len(RANGE))


class TestSelectExtremes(unittest.TestCase):

  def testSimple(self):
    fltr = selectExtremes(RANGE, 1)
    self.assertTrue(fltr[0])
    fltr = selectExtremes(RANGE, 2)
    self.assertFalse(all(fltr))

  def testMore(self):
    values = [1, 3, -1, 2]
    fltr = selectExtremes(values, 1)
    self.assertTrue(fltr[2])
    fltr = selectExtremes(values, 0.5)
    self.assertTrue(fltr == [True, False, True, False])


if __name__ == '__main__':
  unittest.main()


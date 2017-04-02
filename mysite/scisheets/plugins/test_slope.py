"""
Tests for slope
"""

from scisheets.plugins.slope import slope
import unittest
import numpy as np
import scipy as sp


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestIntercept(unittest.TestCase):

  def testBasics(self):
    SIZE = 100
    INTERCEPT = 5
    SLOPE = 3
    SD = 1.0
    tolerance = 4*SD/np.sqrt(SIZE)
    xarray = np.array(range(SIZE), dtype=float)
    yarray = INTERCEPT + SLOPE*xarray + sp.random.normal(0, SD, SIZE)
    computed_slope = slope(xarray, yarray)
    self.assertLessEqual(abs(computed_slope[0] - SLOPE), tolerance)


if __name__ == '__main__':
  unittest.main()

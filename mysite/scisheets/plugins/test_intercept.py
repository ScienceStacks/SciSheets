"""
Tests for intercept
"""

from intercept import intercept
import unittest
import numpy as np
import scipy as sp


# TODO: Create approx equal function
TOLERANCE = 0.01


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestIntercept(unittest.TestCase):

  def testBasics(self):
    size = int((1/TOLERANCE)**3)
    INTERCEPT = 5
    SLOPE = 3
    SD = 1.0
    xarray = np.array(range(size), dtype=float)
    yarray = INTERCEPT + SLOPE*xarray + sp.random.normal(0, SD, size)
    computed_intercept = intercept(xarray, yarray)
    self.assertLessEqual(abs(computed_intercept[0] - INTERCEPT)/INTERCEPT,
        TOLERANCE)

  def test2(self):
    ss = np.array([ 0.01,  0.05,  0.12,  0.2 ,  0.5 ,  1.  ,   np.nan,   np.nan,   np.nan,   np.nan])
    vv = np.array([ 0.11,  0.19,  0.21,  0.22,  0.21,  0.24,   np.nan,   np.nan,   np.nan,   np.nan])
    computed_intercept = intercept(ss, vv)
    expected = 0.172
    self.assertLessEqual(abs(computed_intercept[0] - expected)/expected,
        TOLERANCE)


if __name__ == '__main__':
  unittest.main()

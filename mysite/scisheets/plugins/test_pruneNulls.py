""" Tests for pruneNulls. """

import numpy as np
from pruneNulls import pruneNulls
import unittest


class TestGroupBy(unittest.TestCase):


  def test1(self):
    values = range(4)
    self.assertTrue(pruneNulls(values) == values)
    extended_values = list(values)
    extended_values.append(None)
    self.assertTrue(pruneNulls(extended_values) == values)
    extended_values.append(np.nan)
    self.assertTrue(pruneNulls(extended_values) == values)


if __name__ == '__main__':
  unittest.main()

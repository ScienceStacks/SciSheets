""" Tests for pruneNulls. """

import numpy as np
from prune_nulls import pruneNulls
import unittest


VALUES = range(4)


class TestGroupBy(unittest.TestCase):


  def testSimple(self):
    self.assertTrue(pruneNulls(VALUES) == VALUES)
    extended_values = list(VALUES)
    extended_values.append(None)
    self.assertTrue(pruneNulls(extended_values) == VALUES)
    extended_values.append(np.nan)
    self.assertTrue(pruneNulls(extended_values) == VALUES)

  def testEmbeddedNulls(self):
    extended_values = list(VALUES)
    extended_values.append(None)
    self.assertTrue(pruneNulls(extended_values) == extended_values)

  def testEmbeddedNulls(self):
    extended_values = list(VALUES)
    extended_values.insert(0, None)
    self.assertTrue(pruneNulls(extended_values) == extended_values)

  def test4(self):
    self.assertEqual(len(pruneNulls([np.nan, np.nan])), 0)


if __name__ == '__main__':
  unittest.main()

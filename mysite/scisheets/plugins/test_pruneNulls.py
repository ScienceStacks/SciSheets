""" Tests for pruneNulls. """

import numpy as np
from pruneNulls import pruneNulls
import unittest


VALUES = range(4)


class TestGroupBy(unittest.TestCase):


  def testSimple(self):
    self.assertTrue(pruneNulls(VALUES) == VALUES)
    extended_values = list(VALUES)
    extended_values.append(None)
    self.assertTrue(pruneNulls(extended_values) == VALUES)
    result = pruneNulls(extended_values, 
        required_length=len(VALUES)+1, null_value=None)
    self.assertTrue(result == extended_values)
    extended_values.append(np.nan)
    self.assertTrue(pruneNulls(extended_values) == VALUES)

  def testEmbeddedNulls(self):
    extended_values = list(VALUES)
    extended_values.insert(0, None)
    self.assertTrue(pruneNulls(extended_values) == extended_values)
    self.assertTrue(pruneNulls(extended_values, 3) 
        == extended_values[:3])
    


if __name__ == '__main__':
  unittest.main()

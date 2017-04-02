'''Tests for is_null.'''

import numpy as np
from scisheets.core.helpers.is_null import isNull, isNan
import unittest


# pylint: disable=C0111
# pylint: disable=E1101
class TestUtil(unittest.TestCase):

  def setUp(self):
    pass

  def testIsNan(self):
    self.assertTrue(isNan(np.nan))
    self.assertFalse(isNan(3.0))
    self.assertFalse(isNan(3))
    self.assertFalse(isNan("a"))
    self.assertFalse(isNan([np.nan]))

  def testIsNull(self):
    self.assertTrue(isNull(np.nan))
    self.assertTrue(isNull(None))
    self.assertFalse(isNull(3.0))
    self.assertFalse(isNull(3))
    self.assertFalse(isNull("a"))
    self.assertFalse(isNull([np.nan]))

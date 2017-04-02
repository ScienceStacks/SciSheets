""" Tests for roundValues. """

from scisheets.plugins.roundValues import roundValues
import unittest
import pandas as pd

RANGE = range(4)

class TestRoundValues(unittest.TestCase):


  def testSimple(self):
    values = [n + 0.01 for n in RANGE]
    new_values = roundValues(values, 1)
    self.assertTrue(list(new_values) == RANGE)
    new_values = roundValues(values, 2)
    self.assertTrue(list(new_values) == list(values))

  def testNetedLists(self):
    values = [n + 0.01 for n in RANGE]
    list_values = [values, values]
    new_list_values = roundValues(list_values, 1)
    for lst in new_list_values:
      self.assertTrue(list(lst), RANGE)


if __name__ == '__main__':
  unittest.main()

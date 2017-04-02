""" Tests for filterList """

from scisheets.plugins.filterList import filterList
import unittest


class TestFilterList(unittest.TestCase):

  def testSimple(self):
    values = range(4)
    new_values = filterList(values, [False, False, False, False])
    self.assertTrue(values == new_values)
    new_values = filterList(values, [False, False, False, True])
    self.assertTrue(range(3) == new_values)
    new_values = filterList(values, [True, True, True, True])
    self.assertEqual(len(new_values), 0)


if __name__ == '__main__':
  unittest.main()


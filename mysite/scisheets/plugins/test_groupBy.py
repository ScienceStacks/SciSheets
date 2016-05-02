""" Tests for groupBy. """

from groupBy import groupBy
import unittest
import pandas as pd

RANGE = range(4)
DOUBLE_RANGE = range(2*len(RANGE))


class TestGroupBy(unittest.TestCase):

  def setUp(self):
    a_values = list(RANGE)
    a_values.extend(RANGE)
    b_values = []
    [b_values.extend([n, n]) for n in RANGE]
    val_dict = {'aa': a_values,              \
        'bb': b_values,                      \
        'cc': [0.1*n for n in DOUBLE_RANGE], \
        'dd': [0.01*n for n in DOUBLE_RANGE]
        }
    self.df = pd.DataFrame(val_dict)
        

  def testSimple(self):
    groups, values = groupBy([self.df['aa']], self.df['cc'])
    expected_group = [str(x) for x in RANGE]
    self.assertTrue(groups == expected_group)
    self.assertEqual(values[0], [0,0.4])

  def testTwoCategories(self):
    groups, values = groupBy([self.df['bb'], self.df['aa']], 
        self.df['cc'])
    self.assertEqual(len(groups), len(DOUBLE_RANGE))
    self.assertEqual(len(values[0]), 1)
    adj_values = [lst[0] for lst in values]
    self.assertTrue(adj_values == list(self.df['cc']))


if __name__ == '__main__':
  unittest.main()

""" Tests for groupBy. """

from scisheets.core.helpers_test import TEST_DIR
from scisheets.plugins.groupBy import groupBy
from scisheets.plugins.roundValues import roundValues
import os
import pandas as pd
import numpy as np
import pickle
import unittest

CAT1 = ['a', 'a', 'b', 'b']
CAT2 = ['x', 'y', 'x', 'y']
CAT1_LIST = list(CAT1)
CAT1_LIST.extend(CAT1)
CAT2_LIST = list(CAT2)
CAT2_LIST.extend(CAT2)
RANGE = range(len(CAT1_LIST))


class TestGroupBy(unittest.TestCase):

  def setUp(self):
    val_dict = {'cat1': CAT1_LIST,
                'cat2': CAT2_LIST,
                'bb': RANGE,
                'cc': [0.1*n for n in RANGE],
                'dd': [0.01*n for n in RANGE]
        }
    self.df = pd.DataFrame(val_dict)
        

  def test1(self):
    groups, values = groupBy([self.df['cat1']], self.df['cc'])
    self.assertTrue(set(groups) == set(CAT1))
    self.assertEqual(len(values), len(groups))
    self.assertTrue(list(roundValues(values[0])) == [0, 0.1, 0.4, 0.5])
    self.assertTrue(list(roundValues(values[1])) == [0.2, 0.3, 0.6, 0.7])

  def test2(self):
    cats = [self.df['cat1'], self.df['cat2']]
    groups, values = groupBy(cats, self.df['bb'])
    self.assertTrue(groups == zip(CAT1, CAT2))
    self.assertEqual(len(values), len(groups))
    for idx in range(len(groups)):
      if groups[idx] == ('a', 'x'):
        self.assertTrue(list(values[idx]) == [0, 4])
      if groups[idx] == ('a', 'y'):
        self.assertTrue(list(values[idx]) == [1, 5])
      if groups[idx] == ('b', 'x'):
        self.assertTrue(list(values[idx]) == [2, 6])
      if groups[idx] == ('b', 'y'):
        self.assertTrue(list(values[idx]) == [3, 7])

  # ADD TEST
  def test3(self):
    return
    filepath = os.path.join(TEST_DIR, "test_groupBy.pcl")
    fh = open(filepath, "rb")
    [category_values, grouping_values] = pickle.load(fh)
    fh.close()
    groups, grouped_values = groupBy(category_values, grouping_values)

  # ADD TEST
  def test4(self):
    return
    filepath = os.path.join(TEST_DIR, "test2_groupBy.pcl")
    fh = open(filepath, "rb")
    [category_values, grouping_values] = pickle.load(fh)
    fh.close()
    groups, grouped_values = groupBy(category_values, grouping_values)

  def test5(self):
    category_values = [0, 1, 1, 1, 2, 3]
    grouping_values = [0.069000000000000006, 0.014999999999999999, 0.069000000000000006, 0.021000000000000001, 0.027, 0.027]
    groups, grouped_values = groupBy(category_values, grouping_values)
    self.assertTrue(groups == range(4))

  def test6(self):
    category_values = [u'0', u'1', u'1', u'1', u'2', u'3', u'4']
    grouping_values = [0.069000000000000006, 0.014999999999999999, 0.069000000000000006, 0.021000000000000001, 0.027, 0.027, 0.027, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    groups, grouped_values = groupBy(category_values, grouping_values)
    self.assertEqual(len(groups), 5)


if __name__ == '__main__':
  unittest.main()

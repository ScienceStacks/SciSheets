""" Tests for tabularize. """

from scisheets.core.api import APIFormulas
from scisheets.core.table import Table
from tabularize import tabularize, _delElement
import unittest
import pandas as pd


CATEGORY_COLNM = 'category'
VALUES_COLNM = 'values'


class TestTabularize(unittest.TestCase):

  def setUp(self):
    val_dict = {CATEGORY_COLNM: [ ['x', 'a'], ['x', 'b'], ['y', 'a'], ['y', 'b']],
        VALUES_COLNM:  range(4)
        }
    df = pd.DataFrame(val_dict)
    self.api = APIFormulas(Table("Dummy"))
    self.api.addColumnsToTableFromDataframe(df)

  def testDelElement(self):
    size = 4
    values = range(size)
    for idx in range(size):
      expected_list = list(values)
      del expected_list[idx]
      self.assertTrue(expected_list == _delElement(values, idx))

  def testSimple(self):
    tabularize(self.api, CATEGORY_COLNM, 1, VALUES_COLNM)
    import pdb; pdb.set_trace()


if __name__ == '__main__':
  unittest.main()

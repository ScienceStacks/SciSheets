""" Tests for param. """

from param import param
from scisheets.core import api as api
from scisheets.core import helpers_test as ht
import unittest


class TestParam(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)
    # Param assumes assumes unique column names
    subtable = self.table.childFromName(ht.SUBTABLE_NAME)
    subtable.removeTree()
    #
    self.api = api.APIFormulas(self.table)

  def testParam(self):
    p1 = param(self.api, ht.COLUMN1)
    self.assertEqual(p1, 'one')
    p2 = param(self.api, ht.COLUMN1, row_num=2)
    self.assertEqual(p2, 'two')


if __name__ == '__main__':
  unittest.main()

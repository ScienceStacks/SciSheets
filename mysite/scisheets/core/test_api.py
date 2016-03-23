'''Tests for formulas API'''

from api import API, APIFormulas
import errors as er
import numpy as np
import unittest


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestTable(unittest.TestCase):

  def setUp(self):
    self.sformulas = APIFormulas(object())

  def testAAnd(self):
    return
    b1 = np.array([True, False, True])
    b2 = np.array([False, False, True])
    b = self.sformulas.aAnd(b1, b2)

if __name__ == '__main__':
  unittest.main()

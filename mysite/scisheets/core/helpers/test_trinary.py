'''Tests for Trinary'''

from trinary import Trinary
import unittest
import cell_types


#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestTrinary(unittest.TestCase):

  def setUp(self):
    self.trinary = Trinary([True, 'False', None])

  def testConstructorWithTrinary(self):
    Trinary(self.trinary)

  def testBadConstructor(self):
    with self.assertRaises(TypeError):
      self.trinary = Trinary([True, 33, None])
    with self.assertRaises(TypeError):
      self.trinary = Trinary([True, 'aa', None])

  def testAnd(self):
    aTrinary = Trinary(['True', 'True', False])
    result = self.trinary & aTrinary
    self.assertEqual(result.tolist(), [True, False, False])

  def testOr(self):
    aTrinary = Trinary([None, 'True', False])
    result = self.trinary | aTrinary
    self.assertEqual(result.tolist(), [True, True, None])

  def testNot(self):
    result = -self.trinary
    self.assertEqual(result.tolist(), [False, True, None])
      


if __name__ == '__main__':
  unittest.main()

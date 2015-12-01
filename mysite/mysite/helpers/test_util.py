'''Tests for utility routines.'''

import unittest
import util as ut


class TestFunctions(unittest.TestCase):

  def testConvertType(self):
    self.assertEqual(ut.ConvertType('3'), 3)
    self.assertEqual(ut.ConvertType('3s'), '3s')
    self.assertTrue(abs(ut.ConvertType('3.1') - 3.1) < 0.001)

  def testConvertTypes(self):
    self.assertEqual(ut.ConvertTypes(['3', '3s', '3.1']),
                                    [ 3 , '3s',  3.1  ])

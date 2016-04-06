
"""
Tests for mechaelisMenton
"""

import my_api as api
from mechaelisMenton import mechaelisMenton
import unittest


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestmechaelisMenton(unittest.TestCase):


  def setUp(self):
    
    self.s = api.APIPlugin('/home/ubuntu/SciSheets/mysite/user/guest/tables/mechaelis_menton.pcl')
    self.s.initialize()
    
    
  def testBasics(self):
    
    # Assign column values to global variables
    S = self.s.getColumnValues('S')
    V = self.s.getColumnValues('V')
    V_MAX,K_M = mechaelisMenton(S,V)
    
    self.assertTrue(self.s.compareToColumnValues('V_MAX', V_MAX))
    self.assertTrue(self.s.compareToColumnValues('K_M', K_M))

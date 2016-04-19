"""
Tests for ProcesEff
"""

import my_api as api
from ProcesEff import ProcesEff
import unittest


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestProcesEff(unittest.TestCase):

  def setUp(self):
    self.s = api.APIPlugin('/home/ubuntu/SciSheets/mysite/user/guest/tables/kristen_gene_table.pcl')
    self.s.initialize()
  def testBasics(self):
    # Assign column values to program variables.
    EffData = self.s.getColumnValues('EffData')
    Mean,Std = ProcesEff(EffData)
    self.assertTrue(self.s.compareToColumnValues('Mean', Mean))
    self.assertTrue(self.s.compareToColumnValues('Std', Std))


if __name__ == '__main__':
  unittest.main()
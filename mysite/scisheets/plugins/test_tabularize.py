""" Tests for tabularize. """

from mysite import settings
from scisheets.core.api import APIFormulas, APIPlugin
from scisheets.core.table import Table
from scisheets.core.helpers.is_null import isNan
from tabularize import tabularize, _delElement
import pandas as pd
import os
import unittest


CATEGORY_COLNM = 'category'
VALUES_COLNM = 'values'
SFX_NAMES = ['a', 'b']
OTHER_NAMES = ['x', 'y']
VALUES = range(4)


class TestTabularize(unittest.TestCase):

  def setUp(self):
    cat_values = []
    for o in OTHER_NAMES:
      for s in SFX_NAMES:
        cat_values.append([o, s])
    val_dict = {CATEGORY_COLNM: cat_values,
        VALUES_COLNM:  VALUES,
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
    new_category_colnm = "NewCategory"
    values_colnm_prefix = "Col"
    tabularize(self.api, CATEGORY_COLNM, 1, VALUES_COLNM,
        new_category_colnm=new_category_colnm,
        values_colnm_prefix=values_colnm_prefix)
    table = self.api._table
    self.assertTrue(table.isColumnPresent(new_category_colnm))
    for sfx in SFX_NAMES:
      expected_name = "%s%s" % (values_colnm_prefix, sfx)
      self.assertTrue(table.isColumnPresent(expected_name))
      column = table.columnFromName(expected_name)
      cells = [x for x in column.getCells() if not isNan(x)]
      size = len(VALUES)/len(SFX_NAMES)
      self.assertEqual(len(cells), size)

  def testFromFile1(self):
    filepath = os.path.join(settings.SCISHEETS_TEST_DIR, 
                            "tabularize_test.pcl")
    api = APIPlugin(filepath)
    api.initialize()
    tabularize(api, 'Groups', 1, 'MeanCt',
        new_category_colnm='BioRuns',
        values_colnm_prefix='Gene_')
    BioRuns = api.getColumnValues('BioRuns')
    Gene_I = api.getColumnValues('Gene_I')
    Gene_R1 = api.getColumnValues('Gene_R1')
    Gene_R2 = api.getColumnValues('Gene_R2')


if __name__ == '__main__':
  unittest.main()

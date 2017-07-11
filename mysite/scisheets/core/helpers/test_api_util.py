'''
Tests for API Utilities. These are codes shared with other
files in core.
 '''

from scisheets.core import helpers_test as ht
import mysite.settings as settings
from CommonUtil.util import stripFileExtension
from scisheets.core.helpers_test import TEST_DIR
import api_util as api_util
from extended_array import ExtendedArray
import numpy as np
import os
import unittest

ARRAY_INT = np.array(range(4))
ARRAY_INT_LONG = np.array(range(5))
ARRAY_FLOAT = np.array([0.01*x for x in range(4)])

TESTFILE = "test_api_util.%s" % settings.SCISHEETS_EXT


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestAPIUtil(unittest.TestCase):

  def setUp(self):
    ht.setupTableInitialization(self)

  def testCompareIterables(self):
    float_list = ARRAY_FLOAT.tolist()
    float_list.append(np.nan)
    new_array_float = np.array(float_list)
    self.assertTrue(api_util.compareIterables(ARRAY_FLOAT, new_array_float))
    self.assertFalse(api_util.compareIterables(ARRAY_INT, ARRAY_INT_LONG))
    self.assertFalse(api_util.compareIterables(ARRAY_INT,
        np.array([0.1*n for n in range(4)])))
    self.assertTrue(api_util.compareIterables(ARRAY_INT, ARRAY_INT))
    self.assertTrue(api_util.compareIterables(ARRAY_FLOAT, ARRAY_FLOAT))

  def testCopyTableToFile(self):
    filename = ht.TEST_FILENAME[:-4]  # Exclude ".pcl"
    table = ht.createTable("test_table")
    new_filepath = api_util.copyTableToFile(table, 
                                            filename,
                                            ht.TEST_DIR)   
    path = os.path.join(ht.TEST_DIR, ht.TEST_FILENAME)
    self.assertEqual(stripFileExtension(new_filepath), 
        stripFileExtension(path))
    self.assertTrue(os.path.exists(new_filepath))
    new_table = api_util.readObjectFromFile(new_filepath, verify=False)
    self.assertTrue(table.isEquivalent(new_table))
    os.remove(new_filepath)

  def testWriteObjectToFileAndReadObjectFromFile(self):
    path = os.path.join(TEST_DIR, TESTFILE)
    self.table.setFilepath(path)
    api_util.writeObjectToFile(self.table)
    new_table = api_util.readObjectFromFile(path)
    self.assertTrue(self.table.isEquivalent(new_table))
    #
    self.table.setFilepath(path)
    api_util.writeObjectToFile(self.table)
    new_table = api_util.readObjectFromFile(path)
    self.assertTrue(self.table.isEquivalent(new_table))
    #
    a_dict = {"a": range(5), "b": range(10)}
    api_util.writeObjectToFile(a_dict, filepath=path)
    new_a_dict = api_util.readObjectFromFile(path)
    self.assertEqual(a_dict, new_a_dict)



if __name__ == '__main__':
  unittest.main()

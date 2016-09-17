"""
This program migrates a table from a PCL representation to
an SCI.
"""

from scisheets.core.helpers.api_util import getTableFromFile
from scisheets.core.helpers.serialize_deserialize import serialize
import os
import unittest

def migrate(path):
  """
  :param str path: filepath
  Creates an sci file with an sci extension
  """
  ext = path[-3:]
  if ext.lower() != 'pcl':
    raise ValueError("%s is not a pcl file" % path)
  table = getTableFromFile(path, verify=False)
  json_str = serialize(table)
  new_path = "%s.sci" % path[:-4]
  with open(new_path, "wb") as fh:
    fh.write(json_str)

class DoMigration(unittest.TestCase):

  def testRun(self):
    dir = "/home/ubuntu/SciSheets/mysite/scisheets/core/test_dir"
    path = os.path.join(dir, "testcase_2.pcl")
    migrate(path)
  

if __name__ == '__main__':
  unittest.main()

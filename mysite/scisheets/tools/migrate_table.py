"""
This program migrates a table from a PCL representation to
an SCI.
"""

from scisheets.core.helpers.api_util import readObjectFromFile
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
  try:
    an_object = readObjectFromFile(path)
  except Exception as e:
    import pdb; pdb.set_trace()
    return
  json_str = serialize(an_object)
  new_path = "%s.sci" % path[:-4]
  with open(new_path, "wb") as fh:
    fh.write(json_str)

class DoMigration(unittest.TestCase):

  def testRun(self):
    file_list = ["testcase_1.pcl"]
    base_dir = "/home/ubuntu/SciSheets/mysite"
    dirs = [
            "scisheets/core/test_dir", 
            "user/guest/tables",
            "user/guest/python",
            "scisheets/ui",
           ]
    for dir in dirs:
      this_dir = os.path.join(base_dir, dir)
      files = [ff for ff in os.listdir(this_dir) if ff[-3:] == 'pcl']
      for ff in files:
        path = os.path.join(this_dir, ff)
        try:
          migrate(path)
        except Exception as e:
          import pdb; pdb.set_trace()
          print ("Could not process %s because of %s" % (path, str(e)))
  

if __name__ == '__main__':
  unittest.main()

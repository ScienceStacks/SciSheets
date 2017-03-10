'''Tests for file_access'''

from mysite import settings
import unittest
import mysite.helpers.file_access as fa
import json
import os

TEST_FILE1 = os.path.join(settings.BASE_DIR, 
    'mysite/helpers/test_file_access.tsv')
TEST_FILE2 = os.path.join(settings.BASE_DIR, 
    'mysite/helpers/test_file_access_crd.tsv')

class TestFunctions(unittest.TestCase):

  def testSplitFilename(self):
    NAME = "dummy"
    EXT = "ext"
    FILENAME = "%s.%s" % (NAME, EXT)
    name, ext = fa.SplitFilename(FILENAME)
    self.assertEqual(name, NAME)
    self.assertEqual(ext, EXT)
    name, ext = fa.SplitFilename(NAME)
    self.assertEqual(name, NAME)
    self.assertEqual(ext, "")


class TestFileBase(unittest.TestCase):

  def setUp(self):
    self.filename = TEST_FILE1
    self.colnames = ['x', 'y', 'z']

  def test_constructor(self):
    fb = fa._FileBase(self.filename)
    self.assertEqual(fb._filename, self.filename)
    self.assertEqual(fb._colnames, self.colnames)
    self.assertRaises(fa.FileError, fa._FileBase, 'invalid file')

  def test_OpenFile(self):
    fb = fa._FileBase(self.filename)
    fb._OpenFile()
    self.assertIsNotNone(fb._fh)
    self.assertTrue(len(fb._fh.readline()) > 0)
    fb._fh.close()

  def test_CloseFile(self):
    fb = fa._FileBase(self.filename)
    fb._OpenFile()
    fb._CloseFile()
    self.assertIsNone(fb._fh)


class Test2Json(unittest.TestCase):

  def setUp(self):
    self.filename = TEST_FILE1
    self.colnames = ['x', 'y', 'z']

  def test_ReadAll(self):
    file2json = fa.File2Json(self.filename)
    result = file2json.ReadAll()
    self.assertTrue(isinstance(result, str))
    lst = json.loads(result)
    self.assertEqual(len(lst), 3)
    keys = []
    [keys.extend(ele.keys()) for ele in lst]
    keys = set(keys)


class TestCrdFile2Json(unittest.TestCase):

  def setUp(self):
    self.filename = TEST_FILE2
    self.c2j = fa.CrdFile2Json(self.filename)

  def test_ReadAll(self):
    self.c2j.ReadAll()
    self.assertEqual(len(self.c2j._xcrds), 2)
    self.assertEqual(self.c2j._xcrds[0], 'x1')
    self.assertEqual(self.c2j._xcrds[1], 'x2')
    self.assertEqual(len(self.c2j._ycrds), 2)
    self.assertEqual(self.c2j._ycrds[0], 'y1')
    self.assertEqual(self.c2j._ycrds[1], 'y2')
    self.assertEqual(len(self.c2j._points), 4)
    self.assertEqual(self.c2j._points[2]['x'], 2)
    self.assertEqual(self.c2j._points[2]['y'], 1)
    self.assertEqual(self.c2j._points[2]['value'], 1100)

  def test_GetXCrds(self):
    self.c2j.ReadAll()
    xcrds_json = self.c2j.GetXCrds()
    xrds = json.loads(xcrds_json)
    self.assertEqual(xrds, self.c2j._xcrds)

  def test_GetYCrds(self):
    self.c2j.ReadAll()
    ycrds_json = self.c2j.GetYCrds()
    ycrds = json.loads(ycrds_json)
    self.assertEqual(ycrds, self.c2j._ycrds)

  def test_GetPoints(self):
    self.c2j.ReadAll()
    points_json = self.c2j.GetPoints()
    points = json.loads(points_json)
    result = True
    for point in points:
      v = set([point == p for p in self.c2j._points])
      r = v.issuperset(set([True]))
      result = result & r
    self.assertTrue(result)
    result = True
    for point in self.c2j._points:
      v = set([point == p for p in points])
      r = v.issuperset(set([True]))
      result = result & r
    self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()

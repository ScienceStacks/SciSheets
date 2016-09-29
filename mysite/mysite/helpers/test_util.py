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

  def testRandomWord(self):
    WORDLEN = 7
    word = ut.randomWord(size=WORDLEN)
    self.assertTrue(isinstance(word, str))
    self.assertEqual(len(word), WORDLEN)

  def testRandomWords(self):
    LEN = 10
    self.assertEqual(len(ut.randomWords(LEN)), LEN)

  def testGetFileExtension(self):
    extensions = ['x', 'xy', 'xyz']
    partial_filename = 'dummy'
    for ext in extensions:
      this_ext = ut.getFileExtension("%s.%s" % (partial_filename, ext))
      self.assertEqual(this_ext, ext)
    # Try with no extension
    this_ext = ut.getFileExtension("%s" % partial_filename)
    self.assertIsNone(this_ext)

  def testStripFileExtension(self):
    extensions = ['x', 'xy', 'xyz']
    partial_filename = '/u/dummy/xx'
    for ext in extensions:
      this_partial = ut.stripFileExtension("%s.%s" % (partial_filename, ext))
      self.assertEqual(this_partial, partial_filename)

  def testStripFileExtensionSingleFile(self):
    extensions = ['x', 'xy', 'xyz']
    partial_filename = 'dummy'
    for ext in extensions:
      this_partial = ut.stripFileExtension("%s.%s" % (partial_filename, ext))
      import pdb; pdb.set_trace()
      self.assertEqual(this_partial, partial_filename)

  def testChangeFileExtension(self):

    def createFilepath(ext):
      partial_filename = '/x/y/dummy'
      if ext is None:
        path = partial_filename
      else:
        path = "%s.%s" % (partial_filename, ext)
      return path

    extensions = ['x', 'xy', 'xyz', None]
    for from_ext in extensions:
      from_path = createFilepath(from_ext)
      for to_ext in extensions:
        to_path = createFilepath(to_ext)
        path = ut.changeFileExtension(from_path, to_ext)
        self.assertEqual(path, to_path)
    
    


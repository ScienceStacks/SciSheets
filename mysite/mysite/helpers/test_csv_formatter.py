'''Tests for CSV formatter'''

from mysite import settings
import unittest
import csv_formatter as cf
import json
import os


class TestFunctions(unittest.TestCase):

  def testGeneticCodeAsDict(self):
    result = cf.GeneticCodeAsDict()
    self.assertEqual(len(result), 64)

  # TODO: better assert
  def testGeneticCodeAsNestedDict(self):
    result = cf.GeneticCodeAsNestedDict()
    self.assertGreaterEqual(len(result), 0)

'''Tests for helpers. '''

from helpers import OrderableStrings
import unittest
import errors as er


#############################
# Constants
#############################
STRING1 = "DUMMY1"
STRING2 = "DUMMY2"


#############################
# Tests
#############################
class TestOrderedStrings(unittest.TestCase):
  
  def setUp(self):
    self.os = OrderableStrings()
    self.os.Append(STRING1)
    self.os.Append(STRING2)

  def testConstructor(self):
    os = OrderableStrings()
    self.assertEqual(len(os._orderable_strings), 0)

  def testAppend(self):
    os = OrderableStrings()
    os.Append(STRING1)
    self.assertEqual(os._orderable_strings[STRING1], 0)
    os.Append(STRING2)
    self.assertEqual(os._orderable_strings[STRING2], 1)
    self.assertRaises(er.InternalError, 
        os.Append, STRING2, NoDuplicate=True)
    os.Append(STRING2, NoDuplicate=False)
    self.assertEqual(os._orderable_strings[STRING2], 2)

  def testDelete(self):
    self.os.Delete(STRING1)
    self.assertEqual(self.os._orderable_strings[STRING2], 0)
    self.assertRaises(er.InternalError, self.os.Delete, STRING1)

  def testGetMaxPosition(self):
    self.assertEqual(self.os.GetMaxPosition(), 1)

  def testGetPosition(self):
    self.assertEqual(self.os.GetPosition(STRING1), 0)
    self.assertEqual(self.os.GetPosition(STRING2), 1)

  def testGetString(self):
    self.assertEqual(self.os.GetString(0), STRING1)
    self.assertEqual(self.os.GetString(1), STRING2)

  def testInsert(self):
    self.assertEqual(self.os.GetString(0), STRING1)
    self.assertEqual(self.os.GetString(1), STRING2)


if __name__ == '__main__':
    unittest.main()

'''Tests for Combinatoric Lists'''

from combinatoric_list import CombinatoricList
import unittest


#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestCombinatoricList(unittest.TestCase):

  def setUp(self):
    self._combinatoric = CombinatoricList([False, True])

  def testListsLength(self):
    self.assertEqual(
       CombinatoricList._listsLength([[1, 2, 3], [4, 5, 6]]), 3)
 
  def testVAppend(self):
    lists1 = [[4, 5], [40, 50]]
    lists2 = [[1,2, 3], [10, 20, 30]]
    result = CombinatoricList._vAppend(lists1, lists2)
    list_a = list(lists2[0])
    list_b = list(lists2[1])
    list_a.extend(lists1[0])
    list_b.extend(lists1[1])
    self.assertEqual(result, [list_a, list_b])

  def testRun(self):
    num_list = 4
    result = self._combinatoric.run(num_list)
    for this_list in result:
      self.assertTrue(len(this_list) == 2**num_list)
      list_true = [x for x in this_list if x==True]
      self.assertEqual(len(list_true), 2**(num_list-1))
   

if __name__ == '__main__':
  unittest.main()

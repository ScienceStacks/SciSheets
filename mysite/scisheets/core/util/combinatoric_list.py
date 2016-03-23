"""
Generates a list of lists that are all combinations of a set
of elements.
Consider the elements [F, T] for a truth table. A truth table
for 3 variables has the lists:
L1: F T F T F T F T
L2: F F T T F F T T
L3: F F F F T T T T
"""

class CombinatoricList(object):
  """
  Usage: cl = CombinatricList(elements, num_lists)
         result = cl.run()
  """

  def __init__(self, elements):
    """
    :param list elements: elements to construct in combination
    """
    self._elements = elements

  @staticmethod
  def _listsLength(list_of_lists):
    """
    Computes the length of the lists in a containing list
    :param list list_of_lists: list of lists of the same length
    :return: length
    """
    return len(list_of_lists[0])

  @staticmethod
  def _validateListsLengths(lists1, lists2):
    """
    :param list list1: list of lists
    :param list list2: list of lists
    :raises: ValueError if the two lists aren't the same length
    """
    if len(lists1) == 0 or len(lists2) == 0:
      return
    expected_length = len(lists1[0])
    lists = list(lists1)
    lists.extend(lists2)
    if not all([len(ll) for ll in lists]):
      import pdb; pdb.set_trace()
      raise ValueError("Length of lists must be the same.")

  @staticmethod
  def _vAppend(lists1, lists2):
    """
    Appends each list in list1 to the corresponding list in list2
    :param list list1: list of lists
    :param list list2: list of lists
    :return: list of lists
    :raises: ValueError if the two lists aren't the same length
    """
    CombinatoricList._validateListsLengths(lists1, lists2)
    if len(lists2) == 0:
      return [list(ll) for ll in lists1]
    result = [list(ll) for ll in lists2]
    for idx in range(len(lists1)):
      result[idx].extend(lists1[idx])
    return result

  def run(self, num_lists):
    """
    Compute the list of combinatoric lists.
    :param num_lists: number of lists to construct
    :return: list_of_lists
    """
    cur_lists = [self._elements]
    for _ in range(num_lists-1):
      old_lists = list(cur_lists)
      cur_lists = []
      new_list = []
      for ele in self._elements:
        length = CombinatoricList._listsLength(old_lists)
        new_list.extend([ele]*length)
        cur_lists = CombinatoricList._vAppend(old_lists, cur_lists)
      cur_lists.append(new_list)
    return cur_lists

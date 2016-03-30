"""
Implements a class for trinary logic, the third value being "unknown"
(represented by None).
Trinary objects use the operators:
  & for AND
  | for OR
  - for NOT
"""

import api_util
import util


AND_TRUTHTABLE = {(None, None): None, (None, False): False, (None, True): None,
                  (False, None): False, (False, False): False, (False, True): False,
                  (True, None): None, (True, False): False, (True, True): True}
OR_TRUTHTABLE = {(None, None): None, (None, False): None, (None, True): True,
                  (False, None): None, (False, False): False, (False, True): True,
                  (True, None): True, (True, False): True, (True, True): True}
NOT_TRUTHTABLE = {None: None, False: True, True: False}

class Trinary(object):
  """
  Class implementing trinary logic
  """

  def __init__(self, values):
    """
    :param iterable values: a Trinary or an iterable of XBool and None
    """
    if isinstance(values, Trinary):
      self._values = values.tolist()
    else:
      self._values = Trinary._convert(values)

  @staticmethod
  def _convert(values):
    """
    Converts the _values to a standard format.
    :raises TypeError: if elements are neither XBool or None
    """
    if not all([util.XBool.isXType(x) or (x is None) for x in values]):
      raise TypeError("Trinary values must be XBool or None.")
    result = [True if x in [True, 'True']  \
                   else False if x in [False, 'False'] \
                   else None if (x is None)  \
                   else -2 for x in values]
    if -2 in result:
      import pdb; pdb.set_trace()
    return result

  def tolist(self):
    return self._values
 
  @staticmethod
  def _pad(values1, values2):
    """
    Makes Trinary objects the same length, padding with None
    :param Trinary values1:
    :param Trinary values2:
    :return: lists with appropriate padding
    """
    len1 = len(values1)
    len2 = len(values2)
    if len1 == len2:
      return values1, values2
    none_len = abs(len1 - len2)
    new_values1 = list(values1)
    new_values2 = list(values2)
    if len1 < len2:
      new_values1.extend([None]*none_len)
    else:
      new_values2.extend([None]*none_len)
    return  new_values1, new_values2
    

    return new_bool_array1, new_bool_array2

  def _bool1(self, logic_dict):
    """
    Performs a monadic logical function
    :param dict logic_dict: dictionary describing the truth table
    :return Trinary values:
    """
    return Trinary([logic_dict[x] for x in self._values])

  def _bool2(self, aTrinary, logic_dict):
    """
    Performs a dyadic logical function, handling
    the presence of NONE values.
    :param aTrinary: Trinary object
    :param dict logic_dict: dictionary describing the truth table
    :return np.array (either object or bool):
    """
    new_list1, new_list2 = Trinary._pad(self._values, aTrinary.tolist())
    result = []
    for idx in range(len(new_list1)):
      key = (new_list1[idx], new_list2[idx])
      result.append(logic_dict[key])
    return result

  def __and__(self, aTrinary):
    """
    Performs AND logic function, handling
    the presence of NONE values.
    :param Trinary aTrinary:
    :return: a Trinary
    """
    return Trinary(self._bool2(aTrinary, AND_TRUTHTABLE))

  def __or__(self, aTrinary):
    """
    Performs OR logic function, handling
    the presence of NONE values.
    :param Trinary aTrinary:
    :return: a Trinary
    """
    return Trinary(self._bool2(aTrinary, OR_TRUTHTABLE))

  def __neg__(self):
    """
    Performs NOT logic function, handling
    the presence of NONE values.
    :return: a Trinary
    """
    return Trinary(self._bool1(NOT_TRUTHTABLE))

  def __str__(self):
    return str(self._values)

###################### Other Constants ####################
def makeTrinary(aList):
  return Trinary(alist)
DATACLASS_TRINARY = api_util.DataClass(cls=Trinary, cons=makeTrinary)

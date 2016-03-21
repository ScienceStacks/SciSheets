"""
API for SciSheets. This consists of two parts: the formulas API that is used
in formulas and the plugin API that is used in the python programs that are
used in formulas.
"""

from column import Column
from table import Table
import util


TRUE = 'True'
FALSE = 'False'
AND_TRUTHTABLE = {(None, None): None, (None, FALSE): False, (None, TRUE): None,
                  (FALSE, None): False, (FALSE, FALSE): False, (FALSE, TRUE): False,
                  (TRUE, None): None, (TRUE, FALSE): False, (TRUE, TRUE): True}
OR_TRUTHTABLE = {(None, None): None, (None, FALSE): None, (None, TRUE): True,
                  (FALSE, None): None, (FALSE, FALSE): False, (FALSE, TRUE): True,
                  (TRUE, None): True, (TRUE, FALSE): True, (TRUE, TRUE): True}
XOR_TRUTHTABLE = {(None, None): None, (None, FALSE): None, (None, TRUE): None,
                  (FALSE, None): None, (FALSE, FALSE): False, (FALSE, TRUE): True,
                  (TRUE, None): None, (TRUE, FALSE): True, (TRUE, TRUE): False}
NOT_TRUTHTABLE = {None: None, FALSE: True, TRUE: False}


class ScisheetsAPI(object):
  """
  Code that is common to the formulas and plugin APIs.
  """

  def __init__(self, table):
    self._table = table
    self._column_idx = None


class ScisheetsFormulas(ScisheetsAPI):
  """
  Formulas API
  """

  def setColumnIndex(self, column_idx):
    self._column_idx = column_idx

  def createTruthTable(self, column_names):
    """
    Creates a truth table with all combinations of Boolean
    values for the number of columns provided.
    :param list-of-str column_names: names of columns to create
    """
    pass

  def createColumn(self, column_name, index=None):
    """
    Creates a new column, either just to the right of the
    current column (index=None) are at a specific index.
    :param str column_name: name of the column to create
    :param int index: index where the column is to be placed
    """
    pass

  @staticmethod
  def _convertBooleans(bool_array):
    """
    Converts the array to a string format.
    :param array (bool or object): array
    :return: array of object with -1 for None
    :raises: InvalidType if not a Boolean array
    """
    new_array =  ['True' if y==True else 'False' if y==False 
                    else None if y is None else -2 for y in x]
    if any([x == -2 for x in new_array]):
      raise TypeError
    return new_array
 
  @staticmethod
  def _padArrays(bool_array1, bool_array2):
    """
    Makes arrays the same length
    :param np.array bool_array1:
    :param np.array bool_array2:
    :return: converted and padded bool_array, bool_array
    """
    len1 = len(bool_array1)
    len2 = len(bool_array2)
    if len1 == len2:
      return bool_array1, bool_array2
    none_array = np.repeat(None, abs(len1-len2))
    new_array1 = ScisheetsFormulas._convertBooleans(bool_array1)
    new_array2 = ScisheetsFormulas._convertBooleans(bool_array2)
    list1 = bool_array1.tolist()
    list2 = bool_array2.tolist()
    if len1 < len2:
      list1.extend(none_array)
    else:
      list2.extend(none_array)
    return np.array(list1), np.array(list2)
    

    return new_bool_array1, new_bool_array2

  @staticmethod
  def _bool1(bool_array, logic_dict):
    """
    Performs a monadic logical function, handling
    the presence of NONE values.
    :param np.array (either object or bool) bool_array:
    :param dict logic_dict: dictionary describing the truth table
    :return np.array (either object or bool):
    """
    new_array = ScisheetsFormulas._convertBooleans(bool_array)
    return [logic_dict[x] for x in bool_array]

  @staticmethod
  def _bool2(bool_array1, bool_array2, logic_dict):
    """
    Performs a dyadic logical function, handling
    the presence of NONE values.
    :param np.array (either object or bool) bool_array1:
    :param np.array (either object or bool) bool_array2:
    :param dict logic_dict: dictionary describing the truth table
    :return np.array (either object or bool):
    """
    new_array1, new_array2 = ScisheetsFormulas._padArrays(
      bool_array1, bool_array2)
    result = []
    for idx in range(len(new_array1)):
      key = (new_array1[idx], new_array2[idx])
      result.append(logic_dict[key])
    return result

  def aAnd(self, bool_array1, bool_array2):
    """
    Performs AND logic function, handling
    the presence of NONE values.
    :param np.array (either object or bool) bool_array1:
    :param np.array (either object or bool) bool_array2:
    :return np.array (either object or bool):
    """
    return ScisheetsFormulas._bool2(bool_array1, bool_array2, 
        AND_TRUTHTABLE)

  def aOr(self, bool_array1, bool_array2):
    """
    Performs OR logic function, handling
    the presence of NONE values.
    :param np.array (either object or bool) bool_array1:
    :param np.array (either object or bool) bool_array2:
    :return np.array (either object or bool):
    """
    return ScisheetsFormulas._bool2(bool_array1, bool_array2, 
        OR_TRUTHTABLE)

  def aXor(self, bool_array1, bool_array2):
    """
    Performs OR logic function, handling
    the presence of NONE values.
    :param np.array (either object or bool) bool_array1:
    :param np.array (either object or bool) bool_array2:
    :return np.array (either object or bool):
    """
    return ScisheetsFormulas._bool2(bool_array1, bool_array2, 
        XOR_TRUTHTABLE)

  def aNot(self, bool_array):
    """
    Performs OR logic function, handling
    the presence of NONE values.
    :param np.array (either object or bool) bool_array:
    :return np.array (either object or bool):
    """
    return ScisheetsFormulas._bool1(bool_array, NOT_TRUTHTABLE)



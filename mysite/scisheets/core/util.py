'''Utilities used in core scitable code.'''

import collections
import math
import numpy as np

DTYPE_STRING = '|S1000'

# ToDo: Need tests
def findDatatypeForValues(values):
  """
  Determines the dominate numpy type ignoring None
  :param values: an enumerable
  :return: numpy type
  """
  array = np.array(values)
  if all([isinstance(v, str) for v in array]):
    return '|S1000'  # Maximum string length is 1000
  else:
    return array.dtype

def isNumbers(values):
  """
  :param values: single or multiple values
  :return: True if number; otherwise, fasle.
  """
  if not isinstance(values, collections.Iterable):
    values = [values]
  result = False
  for val in values:
    if isinstance(val, float) or isinstance(val, int):
      result = True
    else:
      try:
        if result and (val is not None) and (not math.isnan(val)):
          return False  # Mixed types
      except TypeError:
        return False
  return result

def isFloats(values):
  """
  :param values: single or multiple values
  :return: True if float or np.nan; otherwise, fasle.
  """
  if not isinstance(values, collections.Iterable):
    values = [values]
  dtype = np.array(values).dtype
  return dtype == np.float64  # pylint: disable=E1101

def makeArray(values):
  """
  Constructs a numpy array from the values, if possible.
  Constructs the most restrictive type (e.g., converting
  strings to Bool,if possible).
  :param values: singleton or iterable of values to make into an array
  :return: a numpy array
  """
  if not isinstance(values, collections.Iterable):
    values = [values]
  array = np.array(values)
  # Test to see if this is a Boolean
  new_values = [True if v == 'True' else
                False if v == 'False' else -1 for v in array]
  if not any([x == -1 for x in new_values]):
    array = np.array(new_values, dtype=np.bool)
  elif array.dtype.type is np.string_:  # pylint: disable=E1101
    array = np.array(values, dtype=DTYPE_STRING)
  return array

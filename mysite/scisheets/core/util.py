'''Utilities used in core scitable code.'''

import collections
import math
import numpy as np

# ToDo: Need tests
def findDatatypeForValues(values):
  """
  Determines the dominate numpy type ignoring None
  :param values: an enumerable
  :return: numpy type
  """
  array =  np.array(values)
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
  return dtype == np.float64

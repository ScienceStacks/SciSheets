'''Utilities used in core scitable code.'''

import collections
import math
import numpy as np

# ToDo: Need tests
def findDatatypeForValues(values):
  """
  Determines the dominate numpy type ignoring None and NaN
  :param values: an enumerable
  :return: numpy type
  """
  for val in values:
    if val is None:
      return object
  for val in values:
    if isinstance(val, str):
      return '|S1000'  # Maximum string length is 1000
    if isinstance(val, float):
      return np.float
    if isinstance(val, int):
      return np.int
  return np.object

def isNumber(values):
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
    

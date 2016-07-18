"""
Eliminate extraneous "null" values, either None or np.nan
"""

from is_null import isNan, isNull
import collections
import numpy as np



def _isStr(val):
  """
  :param object val:
  :return bool:
  """
  return isinstance(val, str) or isinstance(val, unicode)

def _isIterable(val):
  """
  Verfies that the value truly is iterable
  :return bool: True if iterable
  """
  if _isStr(val):
    return False
  return isinstance(val, collections.Iterable)

def pruneNulls(values):
  """"
  Prunes null values from the end of a list
  :param iterable values:
  :returns iterable:
  """
  reverse_values = list(values)
  reverse_values.reverse()
  cur_len = len(values)
  for val in reverse_values:
    if _isIterable(val):
      if any([not isNull(x) for x in val]):
        return values[:cur_len]
    elif not isNull(val):
      return values[:cur_len]
    cur_len -= 1
  return []

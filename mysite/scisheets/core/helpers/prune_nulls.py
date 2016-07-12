"""
Eliminate extraneous "null" values, either None or np.nan
"""

from is_null import isNan, isNull
import collections
import numpy as np

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
    if not isNull(val):
      return values[:cur_len]
    cur_len -= 1
  return []

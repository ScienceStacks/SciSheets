"""
Eliminate extraneous "null" values, either None or np.nan
"""

from scisheets.core.helpers.cell_types import isNull
import collections
import numpy as np

def pruneNulls(values, required_length=None, null_value=np.nan):
  """"
  Prunes null values from the end of a list
  :param iterable values:
  :param int/None required_length: length required for the result
      If None, then trims all excess Null values
  :returns iterable or value:
  """
  reverse_values = list(values)
  reverse_values.reverse()
  found_nonnull = False
  result = []
  for val in reverse_values:
    if found_nonnull:
      result.insert(0, val)
    elif not isNull(val):
      found_nonnull = True
      result.insert(0, val)
  if len(result) < required_length:
    start = len(result)
    finish = required_length
    for idx in range(start, finish):
      result.append(null_value)
  else:
    result = result[:required_length]
  return result
    
    
  return [x for x in values if not isNull(x)]

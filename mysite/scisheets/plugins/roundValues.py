'''Recursively rounds values in a column.'''

import collections
import numpy as np


def roundValues(values, digits=1):
  """
  Rounds values, list of values, etc.
  :param list-of-object values:
  :param int digits: number of digits to round
  :return np.array:
  """
  result = []
  for val in values:
    if isinstance(val, collections.Iterable):
      result.append(roundValues(val))
    elif isinstance(val, float):
      result.append(round(val, digits))
    else:
      result.append(val)
  return np.array(result)

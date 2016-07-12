"""Checks for null values regardless of type."""

import collections
import numpy as np


def isNan(val):
  """
  Checks for NaN even if not float
  :param object val:
  :return bool:
  """
  if isinstance(val, collections.Iterable):
    return False
  try:
    result = np.isnan(val)
  except:
    result = False
  return result

def isNull(val):
  """
  Checks if this is a null value, either None or Nan
  """
  is_nan = isNan(val)
  is_none = val is None
  return is_nan or is_none

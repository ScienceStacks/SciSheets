"""Does comparisons of arrays with None values."""
import numpy as np
import collections

THRESHOLD = 0.01

def compareArrays(arr1, arr2):
  """
  Compares two arrays.
  :param arr1: array or list, possibly with None values
  :param arr2: array or list, possibly with None values
  :return: True if equivalent; otherwise false
  """
  def sameType(val1, val2):
    """
    :param val1, val2: values to compare
    """
    types = [int, float, bool, str]
    if (val1 is None) and (val2 is None):
      return True
    elif (val1 is None) or (val2 is None):
      return False
    result = False
    for typ in types:
      if typ == float:
        if np.isnan(val1) or np.isnan(val2):
          result = np.isnan(val1) == np.isnan(val2)
          break
      if isinstance(val1, typ) and isinstance(val2, typ):
        result = True
        break
    return result

  is_equal = True
  if not isinstance(arr1, collections.Iterable):
    arr1 = np.array([arr1])
  if not isinstance(arr2, collections.Iterable):
    arr2 = np.array([arr2])
  if len(arr1) != len(arr2):
    is_equal = False
  else:
    for idx in range(len(arr1)):
      if not sameType(arr1[idx], arr2[idx]):
        is_equal = False
        break
      elif isinstance(arr1[idx], float):
        if abs(arr1[idx]) < THRESHOLD:
          denom = 1.0
        else:
          denom = arr1[idx]
        if np.isnan(arr1[idx]) != np.isnan(arr2[idx]):
          is_equal = False
          break
        if np.isnan(arr1[idx]) and np.isnan(arr2[idx]):
          break
        elif abs((arr1[idx] - arr2[idx])/denom) > THRESHOLD:
          is_equal = False
          break
      else:
        if arr1[idx] != arr2[idx]:
          is_equal = False
          break
  return is_equal

if __name__ == '__main__':
  IS_OK = not compareArrays(np.array(range(4)),
                            np.array(range(5)))
  IS_OK = IS_OK and not compareArrays(np.array(range(4)),
                             np.array([0.1*n for n in range(4)]))
  IS_OK = IS_OK and compareArrays(np.array(range(4)),
                          np.array(range(4)))
  IS_OK = IS_OK and compareArrays(np.array([n*.01 for n in range(4)]),
                          np.array([n*.01 for n in range(4)]))
  if IS_OK:
    print "OK."
  else:
    print "Test failed."

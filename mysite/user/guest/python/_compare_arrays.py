"""Does comparisons of arrays with None values."""
import numpy as np

def compareArrays(arr1, arr2):
  # Inputs: arr1 - array, possibly with None values
  #         arr2 - array, possible with None values
  # Outputs: True if equivalent; otherwise false
  THRESHOLD = 0.01
  if not isinstance(arr1, np.ndarray):
    arr1 = np.array([arr1])
  if not isinstance(arr2, np.ndarray):
    arr2 = np.array([arr2])
  if len(arr1) != len(arr2):
    return False
  for n in range(len(arr1)):
    if type(arr1[n]) != type(arr2[n]):
      return False
    if isinstance(arr1, float):
      if abs(arr1[n]) < THRESHOLD:
        denom = 1.0
      else:
        denom = arr1[n]
      for m in len(arr1):
        if (arr1[n][m] is None) and (arr2[n][m] is not None):
          return False
        if (arr2[n][m] is None) and (arr2[n][m] is not None):
          return False
      if abs( (arr1[n] - arr2[n])/denom) > THRESHOLD:
        return False
    else:
      if arr1[n] != arr2[n]:
        return False
  return True

if __name__ == '__main__':
  b = not compareArrays(np.array(range(4)),
                   np.array(range(5)))
  b = b and not compareArrays(np.array(range(4)),
                             np.array([0.1*n for n in range(4)]))
  b = b and compareArrays(np.array(range(4)), 
                          np.array(range(4)))
  b = b and compareArrays(np.array([n*.01 for n in range(4)]), 
                          np.array([n*.01 for n in range(4)])) 
  if b:
    print ("OK.")
  else:
    print ("Test failed.")

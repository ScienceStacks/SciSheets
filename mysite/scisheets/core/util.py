'''Utilities used in core scitable code.'''

import numpy as np

# ToDo: Need tests
def findTypeForData(data):
  # Determines the dominate numpy type
  # ignoring None and NaN
  # Inputs: data - an enumerable
  # Outputs: numpy type
  for x in data:
    if isinstance(x, str):
      return '|S1000'  # Maximum string length is 1000
    if isinstance(x, float):
      return np.float
    if isinstance(x, int):
      return np.int
  return np.object

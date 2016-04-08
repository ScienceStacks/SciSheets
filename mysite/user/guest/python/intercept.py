''' 
  Computes the y intercept for a univariate least squares regression.
'''

import numpy as np
import scipy as sp
import scipy.stats as ss


def intercept(xarray, yarray):
  """
  Computes the regression intercept for the x,y pairs
  :param np.array.dtype=float xarray:
  :param np.array.dtype=float yarray:
  """
  _, intercept, _, _, _ = ss.linregress(xarray, yarray)
  result = np.array(np.repeat(np.nan, len(xarray)), dtype=np.float)
  result[0] = intercept
  return result

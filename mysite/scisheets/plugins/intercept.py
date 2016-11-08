''' 
  Computes the y intercept for a univariate least squares regression.
'''

from pruneNulls import pruneNulls
import numpy as np
import scipy as sp
import scipy.stats as ss


def intercept(xarray, yarray):
  """
  Computes the regression intercept for the x,y pairs
  :param np.array.dtype=float xarray:
  :param np.array.dtype=float yarray:
  """
  pruned_x = pruneNulls(xarray)
  pruned_y = pruneNulls(yarray)
  _, intercept, _, _, _ = ss.linregress(pruned_x, pruned_y)
  result = np.array(np.repeat(np.nan, len(xarray)), dtype=np.float)
  result[0] = intercept
  return result

''' 
  Computes the y slope for a univariate least squares regression.
'''

from scisheets.plugins.pruneNulls import pruneNulls
import numpy as np
import scipy as sp
import scipy.stats as ss


def slope(xarray, yarray):
  """
  Computes the regression slope for the x,y pairs
  :param np.array.dtype=float xarray:
  :param np.array.dtype=float yarray:
  """
  pruned_x = pruneNulls(xarray)
  pruned_y = pruneNulls(yarray)
  slope, _, _, _, _ = ss.linregress(pruned_x, pruned_y)
  result = np.array(np.repeat(np.nan, len(xarray)), dtype=np.float)
  result[0] = slope
  return result

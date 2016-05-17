"""
Eliminate extraneous "null" values, either None or np.nan
"""

from scisheets.core.helpers.cell_types import isNull
import collections

def pruneNulls(values):
  """"
  :param iterable:
  :returns iterable or value:
  """
  return [x for x in values if not isNull(x)]

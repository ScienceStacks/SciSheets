"""
Construct removes deletes from a list
"""

from selectExtremes import selectExtremes
from filterList import filterList

def filterExtremes(values, max_std, min_size=1):
  """"
  Returns a new list based on the filter.
  :param list-of-numbers values:
  :param float max_std: maxium standard deviation for the group,
                        subject to constraints on the group size.
  :param int min_size: minimum size for the list of values
  :return list-of-numbers:
  """
  fltr = selectExtremes(values, max_std, min_size=min_size)
  return filterList(values, fltr)

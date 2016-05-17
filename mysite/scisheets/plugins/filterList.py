"""
Construct removes deletes from a list
"""

def filterList(values, filter):
  """"
  Returns a new list based on the filter.
  :param list values:
  :param list-of-bool filter: remove from list if ele is True
  :return list:
  """
  return [x for (x, b) in zip(values, filter) if not b]

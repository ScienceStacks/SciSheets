"""
Get the group names and their values
"""

from pruneNulls import pruneNulls
import collections
import pandas as pd

def groupBy(category_values, grouping_values):
  """"
  Forms groups based on category values.
  :param Iterable-of-Iterable category_values: defines groups
  :param Iterable grouping_values: values in groups
  :return list-of-str/list-of-list-of-str, 
      list-of-list: groups formed and values in each group
  Note: Iterables must have the same length
  """
  idx_data = 'data'
  df = pd.DataFrame()
  df[idx_data] = pruneNulls(grouping_values)
  groupby_list = []
  if isinstance(category_values[0], collections.Iterable):
    for n in range(len(category_values)):
      idx = str(n)
      df[idx] = pruneNulls(category_values[n])
      groupby_list.append(df[idx])
  else:
    idx = str('0')
    df[idx] = pruneNulls(category_values)
    groupby_list.append(df[idx])
  groupby = df[idx_data].groupby(groupby_list)
  groups = [g[0] for g in groupby]
  grouped_values = [list(g[1]) for g in groupby]
  return groups, grouped_values

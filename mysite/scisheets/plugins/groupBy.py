"""
Get the group names and their values
"""

import collections
import pandas as pd

def groupBy(category_values, grouping_values):
  """"
  Forms groups based on category values.
  :param list-of-Iterable category_values: defines groups
  :param Iterable grouping_values: values in groups
  :return list-of-str/list-of-list-of-str, 
      list-of-list: groups formed and values in each group
  Note: Iterables must have the same length
  """
  df_idx = 'A'
  df = pd.DataFrame()
  df[df_idx] = grouping_values
  df_list = list(df['A'].groupby(category_values))
  groups = []
  for idx in range(len(df_list)):
    group = []
    raw_group = df_list[idx][0]
    if isinstance(raw_group, collections.Iterable):
      for ele in df_list[idx][0]:
        group.append(str(ele))
    else:
      group = str(raw_group)
    groups.append(group)
  #groups = [df_list[n][0] for n in range(len(df_list))]
  grouped_values = [list(df_list[n][1]) for n in range(len(df_list))]
  return groups, grouped_values

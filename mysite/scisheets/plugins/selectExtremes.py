"""
Construct a filter that selects extreme values in a list
"""

import numpy as np

def selectExtremes(values, max_std, min_size=1):
  """"
  Returns a selector (boolean list) that selects values
  that are most extreme according to a criteria.
  :param list-of-numbers values:
  :param float max_std: maxium standard deviation for the group,
  subject to constraints on the group size.
  :param int min_size: minimum size for the list of values
  :return list-of-bool: extreme value if bool is true
  """
  def dfm(mean, value):
    return abs(mean-value)

  cur_std = np.std(values, ddof=1)
  length = len(values)
  initial_select = [False for n in range(length)]
  paired_list = zip(initial_select, values)
  iterations = 0
  while iterations < length-min_size:
    new_values = [x for (b, x) in paired_list if not b]
    if np.std(new_values) <= max_std:
      break
    # Eliminate the next largest value
    mean = np.mean(new_values)
    max_idx = 0   
    for idx in range(length):
      (b, x) = paired_list[idx]
      max_val = paired_list[max_idx][1]
      if not b and dfm(x, mean) > dfm(max_val, mean):
        max_idx = idx
    (b, x) = paired_list[max_idx]
    paired_list[max_idx] = (True, x)
    iterations += 1
  (flter, values) = zip(*paired_list)
  return list(flter)

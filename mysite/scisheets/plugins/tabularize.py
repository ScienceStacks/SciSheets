"""
Create a tabular representation of list data that constitute
categorical values.
Below is an example:

  CATEGORICAL      VALUES
  [a, x]           1
  [a, y]           2
  [b, x]           3
  [b, y]           4

The above is tabularized with respect to the first element in 
CATEGORICAL as follows:

  NEW_CATEGORICAL COL_a COL_b
  x                1    3
  y                2    4
"""

import collections
import pandas as pd

def _delElement(an_iterable, idx):
  """
  :param iterable an_iterable:
  :param int idx:
  :return list: list without element idx
  """
  a_list = list(an_iterable)
  new_list = a_list[0:idx]
  back_list = a_list[(idx+1):]
  new_list.extend(back_list)
  return new_list
  

def tabularize(s, 
               category_colnm,
               category_index,
               values_colnm, 
               new_category_colnm=None,
               values_colnm_prefix="New"):
  """
  :param APIObject s:
  :param str category_colnm: name of the category column
  :param int category_index: index of the list elements in the category column
                             to use in defining the new values columns
  :param str values_colnm: name of the column containing values
  :param str new_category_colnm: name of the new category column. Default
                                  is to prepend "New" to the existing name
  :param str values_colnm_prefix: Prefix that prepends the new values column
  """
####### FIX SO CATEGORY COLUMN ALIGNS WITH VALUES:w

  if new_category_colnm is None:
    new_category_colnm = "New%s" % category_colnm
  category_elements = s.getColumnValues(category_colnm)
  values = s.getColumnValues(values_colnm)
  if len(category_elements) != len(values):
    raise ValueError('Unequal lengths for cateogry column %s and values column %s' %  \
        (category_colnm, values_colnm))
  new_category_elements = []
  category_suffixes = set([ele[category_index] for ele in category_elements])
  new_frame = {}
  new_category = set([_delElement(ele, category_index) for ele in category_elements])
  for cat in category_suffixes:
    new_frame[cat] = [np.nan for n in len(values)]
  new_frame[new_category_colnm] = []
  for new_cat in new_category:
    new_frame[new_category_colnm].append(new_cat)
  for idx in range(len(values)):
    full_cat = category_elements[idx]
    colnm_cat = full_cat[idx]
    new_cat = _delElement(full_cat, category_index)
    new_frame[cat].append(values[idx])
  for cat in category_suffixes:
    name = "%s%s" % (values_colnm_prefix, str(cat))
    s.createColumn(name)
    s.setColumnValues(name, new_values[cat])
  s.createColumn(new_category_colnm)
  s.setColumnValues(new_category_colnm, new_elements)
  

  

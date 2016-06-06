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

from scisheets.core.helpers.cell_types import isNull
import collections
import numpy as np

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

def _uniqueElements(an_iterable):
  """
  :param iterable an_iterable:
  :param int idx:
  :return list: has only one occurrence of each element
  """
  used = []
  unique = [x for x in an_iterable if x not in used and (used.append(x) or True)]
  return unique
  

def tabularize(s, 
               category_colnm,
               category_index,
               values_colnm, 
               new_category_colnm=None,
               values_colnm_prefix="Col"):
  """
  :param APIObject s:
  :param str category_colnm: name of the category column with cells that
                             have a list of category values
  :param int category_index: index of the list elements in the category column
                             to use in defining the new values columns
  :param str values_colnm: name of the column containing values
  :param str new_category_colnm: name of the new category column. Default
                                  is to prepend "New" to the existing name
  :param str values_colnm_prefix: Prefix that prepends the new values column
  Creates the column variables corresponding to the new columns.
  """
  # Initializations
  if new_category_colnm is None:
    new_category_colnm = "New%s" % category_colnm
  raw_category_elements = s.getColumnValues(category_colnm)
  raw_values = s.getColumnValues(values_colnm)
  pairs = zip(raw_category_elements, raw_values)
  category_elements = []
  values = []
  for cat, val in pairs:
    if not isNull(cat):
      category_elements.append(cat)
      values.append(val)
  size = len(values)
  # Construct the column values
  col_dict = {}
  elements = [_delElement(ele, category_index) for ele in category_elements]
  col_dict[new_category_colnm] = _uniqueElements(elements)
  new_length = len(col_dict[new_category_colnm])
  colnm_suffixes = set([ele[category_index] for ele in category_elements])
  for sfx in colnm_suffixes:
    col_dict[sfx] = [np.nan for n in range(new_length)]
  for idx in range(len(values)):
    cur_cat = category_elements[idx]
    sfx = cur_cat[category_index]
    new_cat = _delElement(cur_cat, category_index)
    row_idx = col_dict[new_category_colnm].index(new_cat)
    col_dict[sfx][row_idx] = values[idx]
  for sfx in colnm_suffixes:
    name = "%s%s" % (values_colnm_prefix, str(sfx))
    s.createColumn(name)
    s.setColumnValues(name, col_dict[sfx])
    s.assignColumnVariable(name)
  s.createColumn(new_category_colnm)
  s.setColumnValues(new_category_colnm, 
                    col_dict[new_category_colnm])
  s.assignColumnVariable(new_category_colnm)

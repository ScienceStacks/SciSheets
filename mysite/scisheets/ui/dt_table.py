'''
  YUI DataTable specific rendering of tables
'''

from django.shortcuts import render
from django.template.loader import get_template
import mysite.settings as settings
import common_tree.named_tree as named_tree
from scisheets.core.helpers.api_util import getFileNameWithoutExtension
from scisheets.core.helpers.cell_types import isFloats, isStr
from scisheets.core.column import Column
from ui_table import UITable
from mysite import settings as st
from common_util import util as ut
import collections
import json
import numpy as np
import random

HTML_SEPARATOR = "-"  # Seperator used in html names
LABEL_HIDDEN = "..."  # Label used for root hidden columns


def makeJSData(data):
  """
  Creates a javascript array by row from the input data, handling
  columns of different lengths.
  :param list-of-list-of-object: list of column values
  :return list-of-list-of-object: list of row values
  """
  def findNumberOfRows(data):
    number_of_rows = 0
    if len(data) > 0:
      for item in data:
        number_of_rows = max(number_of_rows, len(item))
    return number_of_rows
    
  # Initializations
  number_of_columns = len(data)
  new_data = [c if isinstance(c, list) else [c] for c in data]
  number_of_rows = findNumberOfRows(new_data)
  # Construct the output
  result = []
  for r in range(number_of_rows):
    row = []
    for c in range(number_of_columns):
      if len(new_data[c]) - 1 < r:
        item = ""  # Handle ragged columns
      else:
        item = new_data[c][r]
      value = str(item)  # Assume use item as-is
      if (item is None):
        value = ""
      elif isFloats(item) and not isinstance(item, collections.Iterable):
        if np.isnan(float(item)):
          value = ""
        else:
          value = str(item)
      elif isStr(item): 
        if item == 'nan':
          value = ""
      row.append(value)
    result.append(row)
  return result


class DTTable(UITable):
  """
  Does rendersing specific to YUI DataTable
  """

  def __init__(self, name):
    super(DTTable, self).__init__(name)

  def getSerializationDict(self, class_variable):
    """
    :param str class_variable: key to use for the class name
    :return dict: dictionary encoding the object
    """
    serialization_dict =   \
        super(DTTable, self).getSerializationDict(class_variable)
    serialization_dict[class_variable] = str(self.__class__)
    return serialization_dict

  @classmethod
  def deserialize(cls, serialization_dict, instance=None):
    """
    Deserializes an UITable object and does fix ups.
    :param dict serialization_dict: container of parameters for deserialization
    :return UITable:
    """
    if instance is None:
      dt_table = DTTable(serialization_dict["_name"])
    super(DTTable, cls).deserialize(serialization_dict,
        instance=dt_table)
    return dt_table

  def copy(self, instance=None):
    """
    Returns a copy of this object
    :param DTTable instance:
    """
    # Create an object if one is not provided
    if instance is None:
      instance = DTTable(self.getName(is_global_name=False))
    # Copy properties from inherited classes
    instance = super(DTTable, self).copy(instance=instance)
    # Set properties from this class
    return instance

  def isEquivalent(self, other, is_exception=False):
    """
    :param UITable other:
    :param bool is_exception: generate an AssertionError if false
    :return bool:
    """
    return super(DTTable, self).isEquivalent(other, 
        is_exception=is_exception)

  @staticmethod
  def fromHTMLToPythonName(html_name):
    """
    Converts the HTML name to a python name.
    :param str html_name:
    """
    python_name = html_name.replace(HTML_SEPARATOR, 
        named_tree.GLOBAL_SEPARATOR)
    return python_name

  @staticmethod
  def fromPythonToHTMLName(python_name):
    """
    Converts the python name to an HTML name.
    :param str python_name:
    """
    html_name = str(python_name).replace(named_tree.GLOBAL_SEPARATOR,
        HTML_SEPARATOR)
    return html_name

  @staticmethod
  def _formatStringForJS(in_string):
    """
    Formats the string so that it can be assigned as a value 
    in javascript
    Input: in_string - string to format
    Output: formated string
    """
    return '`%s`' % str(in_string)

  @staticmethod
  def _formatFormula(formula):
    """
    Formats a formula for the web page
    :param str formula:
    :return str: formatte formula
    """
    if formula is None or (formula == "None"):
      result = "''"
    else:
      result = DTTable._formatStringForJS(formula)
    return result

  def _getExcludedNameColumns(self):
    """
    Returns a list of name columns that are to be excluded from
    rendering because they belong to attached tables.
    """
    result = []
    for column in self.getColumns():
      if not column.getParent().isAttached():
        continue
      if column.getParent() == column.getRoot(is_attached=False):
        continue
      if DTTable.isNameColumn(column):
        result.append(column)
    return result

  def _createRecursiveChildrenDict(self, label_dict, 
      excludes=None, children_dict=None,
      sep=named_tree.GLOBAL_SEPARATOR):
    """
    Creates a recursive parent-child structure.
    :param dict label_dict: key is global name, value is label
    :param list-of-Tree excludes: list of nodes to exclude from list
    :param ChildrenDict children_dict:
    :param str sep: separator in components of global name
    :return recursive dictionary: keys = {name, label, children} 
    """
    if children_dict is None:
      children_dict = self.getChildrenBreadthFirst(excludes=excludes)
    if excludes is None:
      excludes = []
    node = children_dict["node"]
    if node == node.getRoot(is_attached=False):
      key = node.getName(is_global_name=False)
      label_dict[key] = key
    else:
      key = node.getName()
    name = key.replace('.', sep)
    result = {"name": name, "label": label_dict[key]}
    dicts = []
    for this_dict in children_dict["children"]:
      if this_dict["node"] in excludes:
        continue
      dicts.append(self._createRecursiveChildrenDict(
          label_dict,
          excludes=excludes, 
          children_dict=this_dict,
          sep=sep))
    result["children"] = dicts
    return result

  def _createLabels(self):
    """
    Creates a dictionary of the labels for the nodes.
    :return dict: key is global name, value is label.
    """
    label_dict = {}
    for child in self.getChildren(is_from_root=True,
        is_recursive=True):
      key = child.getName()
      if child in self.getVisibleNodes():
        name = child.getName(is_global_name=False)
        prefix = ""
        suffix = ""
        if isinstance(child, Column):
          if child.getFormula() is not None:
            prefix = "*"
        elif not child.isAttached():
          prefix = "[%s" % prefix
          suffix = "%s]" % suffix
        value = "%s%s%s" % (prefix, name, suffix)
        label_dict[key] = value
      else:
        label_dict[key] = LABEL_HIDDEN
    return label_dict

  def render(self, table_id="scitable"):
    """
    Renders the table for a YAHOO DataTable.
    For hierarchical tables:
      a) columnDefs may have children, and array with name 'children'
      b) leafColumns should be a list of columns with data (leaf nodes)
      c) dataSource should be a list of values (not a dict) in the same
         order as the leafColumns
      d) Detached subtables are rendered with a ' ' column on either
         side and do render the row column
      e) Attached subtables do not have their row column rendered
    Input: table_id - how the table is identified in the HTML
    Output: html rendering of the Table
    Note: Full column name uses a '-' seperator instead of '.'
          because of HTML's handling of '.' in names.
    """
    descendents = self.getAllNodes()
    descendents.remove(self)  # Don't include the root name
    excluded_name_columns = self._getExcludedNameColumns()
    columns = [c for c in descendents 
        if c in self.getVisibleNodes() and not c in excluded_name_columns]
    leaves = DTTable.findLeavesInNodes(columns)
    column_labels = [c.getName(is_global_name=False) for c in columns]
    column_names = [DTTable.fromPythonToHTMLName(c.getName()) for c in columns]
    hiddens = self.getHiddenNodes()
    hidden_roots = DTTable.findRootsInNodes(hiddens)
    leaves.extend(hidden_roots)
    excludes = list(set(hiddens).difference(set(hidden_roots)))
    excludes.extend(excluded_name_columns)
    label_dict = self._createLabels()
    column_hierarchy = self._createRecursiveChildrenDict(
        label_dict, excludes=excludes, sep=HTML_SEPARATOR)
    column_hierarchy = column_hierarchy["children"]
    js_column_hierarchy = json.dumps(column_hierarchy)
    js_column_hierarchy = js_column_hierarchy.replace('"name"', 'name')
    js_column_hierarchy = js_column_hierarchy.replace('"children"', 'children')
    js_column_hierarchy = js_column_hierarchy.replace('"label"', 'label')
    js_data = str(makeJSData([l.getCells() if (isinstance(l, Column) and 
        (l not in hidden_roots)) else [] for l in leaves]))
    formula_dict = {}
    for column in self.getVisibleColumns():
      key = DTTable.fromPythonToHTMLName(column.getName())
      formula_dict[key] =  \
          DTTable._formatFormula(column.getFormula())
    table_file = getFileNameWithoutExtension(self.getFilepath())
    formatted_epilogue = DTTable._formatFormula(self.getEpilogue().getFormula())
    formatted_prologue = DTTable._formatFormula(self.getPrologue().getFormula())
    leaf_names = [DTTable.fromPythonToHTMLName(c.getName()) for c in leaves]
    response_schema = str(leaf_names)
    ctx_dict = {'response_schema': response_schema,
                'data': js_data,
                'epilogue': formatted_epilogue,
                'column_hierarchy': js_column_hierarchy,
                'formula_dict': formula_dict,
                'prologue': formatted_prologue,
                'table_caption': self.getName(is_global_name=False),
                'table_file': DTTable._formatStringForJS(table_file),
                'table_id': table_id,
               }
    html = get_template('scitable.html').render(ctx_dict)
    return html

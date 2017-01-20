'''
  YUI DataTable specific rendering of tables
'''

from django.shortcuts import render
from django.template.loader import get_template
import mysite.settings as settings
import mysite.helpers.named_tree as named_tree
from scisheets.core.helpers.api_util import getFileNameWithoutExtension
from scisheets.core.helpers.cell_types import isFloats, isStr
from scisheets.core.column import Column
from ui_table import UITable
from mysite import settings as st
from mysite.helpers import util as ut
import collections
import json
import numpy as np
import random

HTML_SEPARATOR = "-"  # Seperator used in html names


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

  @classmethod
  def createRandomTable(cls, name, nrow, ncol, ncolstr=0,
        low_int=0, hi_int=100):
    """
    Creates a table with random integers as values
    Input: name - name of the table
           nrow - number of rows
           ncol - number of columns
           ncolstr - number of columns with strings
           low_int - smallest integer
           hi_int - largest integer
    """
    table = super(DTTable, cls).createRandomTable(name, nrow, ncol,
        ncolstr=ncolstr, low_int=low_int, hi_int=hi_int,
        table_cls=cls)
    table.setFilepath(settings.SCISHEETS_DEFAULT_TABLEFILE)
    return table

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

  def isEquivalent(self, other):
    return super(DTTable, self).isEquivalent(other)

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

  def _makeColumnDefinitions(self):
    """
    Creates the column definition text string
    :return JSON str:
    """
    last_node = self.getRoot()
    #for nodes in self.getVisibleNodes():

  def _getExcludedNameColumns(self):
    """
    Returns a list of name columns that are to be excluded from
    rendering because they belong to attached tables.
    """
    result = []
    for column in self.getColumns():
      if not column.getParent().isAttached():
        continue
      if column.getParent() == column.getRoot():
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
    if node == node.getRoot():
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
      if child in self.getVisibleNodes():
        key = child.getName()
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
    column_names = [c.getName(is_global_name=False) for c in columns]
    excludes = self.getHiddenNodes()
    excludes.extend(excluded_name_columns)
    label_dict = self._createLabels()
    column_hierarchy = self._createRecursiveChildrenDict(
        label_dict, excludes=excludes, sep=HTML_SEPARATOR)
    column_hierarchy = column_hierarchy["children"]
    js_column_hierarchy = json.dumps(column_hierarchy)
    js_column_hierarchy = js_column_hierarchy.replace('"name"', 'name')
    js_column_hierarchy = js_column_hierarchy.replace('"children"', 'children')
    js_column_hierarchy = js_column_hierarchy.replace('"label"', 'label')
    js_data = str(makeJSData([c.getCells() for c in leaves]))
    raw_formulas = [c.getFormula() if isinstance(c, Column) else None
                    for c in self.getVisibleNodes()]
    formulas = [DTTable._formatFormula(ff) for ff in raw_formulas]
    formula_dict = {}
    for nn in range(len(column_names)):
      formula_dict[column_names[nn]] = formulas[nn]
    table_file = getFileNameWithoutExtension(self.getFilepath())
    formatted_epilogue = DTTable._formatFormula(self.getEpilogue().getFormula())
    formatted_prologue = DTTable._formatFormula(self.getPrologue().getFormula())
    leaf_names = [str(c.getName()).replace('.', HTML_SEPARATOR)
        for c in leaves]
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

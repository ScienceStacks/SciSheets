'''
  YUI DataTable specific rendering of tables
'''

from django.shortcuts import render
from django.template.loader import get_template
from mysite.helpers.versioned_file import VersionedFile
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

HTML_SEPERATOR = "-"  # Seperator used in html names


def makeJSData(data):
  """
  Creates a javascript array by row from the input data, handling
  columns of different lengths.
  :param list-of-list-of-object: list of column values
  :return list-of-list-of-object: list of row values
  """
  # Initializations
  number_of_columns = len(data)
  if len(data) > 0:
    if isinstance(data[0], list):
      number_of_rows = len(data[0])
    else:
      number_of_rows = 1
  else:
    number_of_rows = 0
  # Convert to list of lists
  new_data = [c if isinstance(c, list) else [c] for c in data]
  # Construct the output
  result = []
  for r in range(number_of_rows):
    row = []
    for c in range(number_of_columns):
      if isinstance(new_data[c], list):
        if len(new_data[c]) - 1 < r:
          item = ""  # Handle ragged columns
        else:
          item = new_data[c][r]
      else:
        item = new_data[c]
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
    python_name = html_name.replace(HTML_SEPERATOR, 
        named_tree.SEPERATOR)
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

  # TBD: How handle multiple name columns?
  def _makeAnnotatedDepthFirstTreeRepresentation(self):
    """
    Creates a list of visible nodes from the root in depth first
    order, where each element has the node name and its position
    relative to the last node.
    :returns list-of-dict: keys:
        name: name of node
        direction: direction in which node is placed in
            tree: 1 (child), 0 (sibling), -1 (parent)
    """
    result = []
    nodes = self.getVisibleNodes()
    last_node = self.getRoot()
    for node in nodes:
      if node.getParent() == last_node:
        direction = 1
      elif last_node.getParent() == node:
        direction = -1
      else:
        direction = 0
      result.append({"name": node.getName(is_global_name=False), 
                     "direction": direction})
      last_node = node
    return result

  def render(self, table_id="scitable"):
    """
    Renders the table for a YAHOO DataTable.
    For hierarchical tables:
      a) columnDefs may have children, and array with name 'children'
      b) leafColumns should be a list of columns with data (leaf nodes)
      c) dataSource should be a list of values (not a dict) in the same
         order as the leafColumns
    Input: table_id - how the table is identified in the HTML
    Output: html rendering of the Table
    Note: Full column name uses a '-' seperator instead of '.'
          because of HTML's handling of '.' in names.
    """
    colnm_dict = {}
    for col in self.getChildren(is_from_root=True,
        is_recursive=True):
      if col in self.getVisibleColumns():
        name = col.getName(is_global_name=False)
        annotate = ""
        if col.getFormula() is not None:
          annotate = "*"
        value = "%s%s" % (annotate, name)
        colnm_dict[name] = value
    descendents = self.getAllNodes()
    descendents.remove(self)  # Don't include the root name
    columns = [c for c in descendents if c in self.getVisibleColumns()]
    column_names = [c.getName(is_global_name=False) for c in columns]
    column_hierarchy = self.getRoot().createSubstitutedChildrenDict(
        colnm_dict, excludes=self.getRoot().getHiddenColumns(), 
        sep=HTML_SEPERATOR)
    column_hierarchy = column_hierarchy["children"]
    js_column_hierarchy = json.dumps(column_hierarchy)
    js_column_hierarchy = js_column_hierarchy.replace('"name"', 'name')
    js_column_hierarchy = js_column_hierarchy.replace('"children"', 'children')
    js_column_hierarchy = js_column_hierarchy.replace('"label"', 'label')
    js_data = str(makeJSData([c.getCells() for c in columns]))
    raw_formulas = [c.getFormula() for c in self.getVisibleColumns()]
    formulas = [DTTable._formatFormula(ff) for ff in raw_formulas]
    formula_dict = {}
    for nn in range(len(column_names)):
      formula_dict[column_names[nn]] = formulas[nn]
    table_file = getFileNameWithoutExtension(self.getFilepath())
    formatted_epilogue = DTTable._formatFormula(self.getEpilogue().getFormula())
    formatted_prologue = DTTable._formatFormula(self.getPrologue().getFormula())
    leaf_names = [str(c.getName()).replace('.', HTML_SEPERATOR)
                  for c in self.getLeaves(is_from_root=True) 
                  if c in self.getVisibleColumns()]
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

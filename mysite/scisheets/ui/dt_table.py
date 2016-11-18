'''
  YUI DataTable specific rendering of tables
'''

from django.shortcuts import render
from django.template.loader import get_template
from mysite.helpers.versioned_file import VersionedFile
import mysite.settings as settings
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


# TODO: Can this be just a list of values in order of column names?
def makeJSON(column_names, data):
  """
  Creates a valid JSON for javascript in
  the format expected by YUI datatable
  Input: column_names - list of variables
         data - list of array data or a list of values
  Output: result - JSON as an array
  """
  number_of_columns = len(column_names)
  if len(data) > 0:
    if isinstance(data[0], list):
      number_of_rows = len(data[0])
    else:
      number_of_rows = 1
  else:
    number_of_rows = 0
  result = "["
  for r in range(number_of_rows):
    result += "{"
    for c in range(number_of_columns):
      if isinstance(data[c], list):
        if len(data[c]) - 1 < r:
          item = ""  # Handle ragged columns
        else:
          item = data[c][r]
      else:
        item = data[c]
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
      result += '`' + value + '`'
      if c != number_of_columns - 1:
        result += ","
      else:
        result += "}"
    if r < number_of_rows -1:
      result += ","
  result += "]"
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
    ncol = int(ncol)
    nrow = int(nrow)
    table = cls(name)
    ncolstr = min(ncol, ncolstr)
    ncolint = ncol - ncolstr
    c_list = range(ncol)
    random.shuffle(c_list)
    for n in range(ncol):
      column = Column("Col_" + str(n))
      if c_list[n] <= ncolint - 1:
        values = np.random.randint(low_int, hi_int, nrow)
        values_ext = values.tolist()
      else:
        values_ext = ut.randomWords(nrow)
      #values_ext.append(None)
      column.addCells(np.array(values_ext))
      table.addColumn(column)
    versioned_file = VersionedFile(
        settings.SCISHEETS_DEFAULT_TABLEFILE,
        st.SCISHEETS_USER_TBLDIR_BACKUP,
        st.SCISHEETS_MAX_TABLE_VERSIONS)
    table.setVersionedFile(versioned_file)
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
    for nodes in self.getVisibleNodes():
      TBD

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
    """
    column_names = []
    for column in self.getVisibleColumns():
      if column.getFormula() is not None:
        name = "*%s" % column.getName()
      else:
        name = column.getName()
      column_names.append(name)
    column_data = [c.getCells() for c in self.getVisibleColumns()]
    raw_formulas = [c.getFormula() for c in self.getVisibleColumns()]
    formulas = [DTTable._formatFormula(ff) for ff in raw_formulas]
    formula_dict = {}
    for nn in range(len(column_names)):
      formula_dict[column_names[nn]] = formulas[nn]
    data = makeJSON(column_names, column_data)
    indicies = range(len(column_names))
    table_file = getFileNameWithoutExtension(self.getFilepath())
    formatted_epilogue = DTTable._formatFormula(self.getEpilogue().getFormula())
    formatted_prologue = DTTable._formatFormula(self.getPrologue().getFormula())
    ctx_dict = {'column_names': column_names,  # Delete
                #'column_tree': column_tree,  # New
                #'leaf_columns': leaf_column_names, # New
                'count': 1,
                'data': data,  # List of values
                'epilogue': formatted_epilogue,
                'final_column_name': column_names[-1],
                'formula_dict': formula_dict,
                'num_cols': len(column_names),
                'prologue': formatted_prologue,
                'table_caption': self.getName(is_global_name=False),
                'table_file': DTTable._formatStringForJS(table_file),
                'table_id': table_id,
               }
    html = get_template('scitable.html').render(ctx_dict)
    return html

'''The file handles the logic of the views'''

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from ..core.column import Column
from ..ui.ui_table import UITable
import mysite.helpers.util as ut
import json
import numpy as np
import os
import pickle
import tempfile

PICKLE_KEY = "pickle_file"
USE_LOCAL_FILE = True
LOCAL_FILE = "scisheet_table.pcl"


# ******************** Helper Functions *****************
def extractDataFromRequest(request, key, convert=False, listvar=False):
  # Returns the value of the key
  if request.GET.has_key(key):
    if listvar:
      return request.GET.getlist(key)
    elif convert:
      return ut.ConvertType(request.GET.get(key))
    else:
      return request.GET.get(key)
  else:
    return None

def createCommandDict(request):
  # Creates a dictionary from the fields in the request
  # that constitute the JSON structure sent in the command
  # from AJAX.
  # Input: request - HTML request object
  # Output: cmd_dict - dictionary of the command
  #  TARGET  COMMAND   DESCRIPTION
  #   Table   Export   Export the table into python
  #   Table   Trim     Remove None rows from the end of the table
  #   Cell    Update   Update the specified cell
  #   Column  Append   Add a new column to the right of the current
  #   Column  Insert   Add a new column to the left of the current
  #   Column  Delete   Delete the column
  #   Column  Formula  Change the column's formula
  #   Column  Move     Move the column to another position
  #                      The name LAST is used for last column
  #   Column  Rename   Rename the column
  #   Row     Append   Add a new row after the current row
  #   Row     Insert   Add a new row before the current row
  #   Row     Move     Move the row to the specified position
  cmd_dict = {}
  cmd_dict['command'] = extractDataFromRequest(request, 'command')
  cmd_dict['target'] = extractDataFromRequest(request, 'target')
  cmd_dict['table_name'] = extractDataFromRequest(request, 'table')
  cmd_dict['args'] = extractDataFromRequest(request, 'args[]', listvar=True)
  cmd_dict['column_index'] = extractDataFromRequest(request, 
      'column', convert=True)
  row_name = extractDataFromRequest(request, 'row')
  if row_name is not None and len(str(row_name)) > 0:
    cmd_dict['row_index'] = UITable.rowIndexFromName(row_name)
  else:
    cmd_dict['row_index'] = None  # Handles case where "row" is absent
  cmd_dict['value'] = extractDataFromRequest(request, 'value',
      convert=True)
  if cmd_dict['row_index'] == -1:
    import pdb; pdb.set_trace()
  return cmd_dict

def _getTable(pickle_file):
  return pickle.load( open(pickle_file, "rb"))

def unPickleTable(request):
  # Returns the table if found
  if request.session.has_key(PICKLE_KEY):
    pickle_file = request.session.get(PICKLE_KEY)
    if not os.path.isfile(pickle_file):
      return None
    else:   
      return _getTable(pickle_file)
  else:
    return None

def pickleTable(request, table):
  if USE_LOCAL_FILE:
    request.session[PICKLE_KEY] = LOCAL_FILE
  else:
    if not request.session.has_key(PICKLE_KEY):
      fh = tempfile.NamedTemporaryFile()
      request.session[PICKLE_KEY] = fh.name  # Just get the name
      fh.close()
  pickle.dump(table, open(request.session[PICKLE_KEY], "wb"))


# ******************** Command Processing *****************
def scisheets(request, ncol, nrow):
  # Creates a new table with the specified number of columns and rows
  # considering the number of rows with strings
  ncol = int(ncol)
  nrow = int(nrow)
  ncolstr = int(ncol/2)
  new_ncol = ncol - ncolstr
  table = UITable.createRandomTable("Demo", nrow, ncol, 
      ncolstr=ncolstr)
  html = table.render()
  pickleTable(request, table)
  return HttpResponse(html)

# Only neeed for "tryajax"
#def scisheets_command(request, _, __):
#  # Handles case where command is invoked with arguments
#  return scisheets_command0(request)

def scisheets_command0(request):
  # Invoked from Ajax within the page with a command structure
  # Input: request - includes command structure in the GET
  # Output returned - 
  cmd_dict = createCommandDict(request)
  table = unPickleTable(request)
  command_result = table.processCommand(cmd_dict)
  json_str = json.dumps(command_result)
  pickleTable(request, table)  # Save table modifications
  return HttpResponse(json_str, content_type="application/json")

def scisheets_reload(request):
  # Invoked to reload the current page
  pickle_file = request.session.get(PICKLE_KEY)
  table = unPickleTable(request)
  if table is None:
    html = "No session found"
  else:
    table.evaluate()
    html = table.render()
  return HttpResponse(html)

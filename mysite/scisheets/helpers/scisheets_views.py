'''The file handles the logic of the views'''

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from ..core.column import Column
from ..ui.ui_table import UITable
import json
import numpy as np
import os
import pickle
import tempfile

PICKLE_KEY = "pickle_file"


# ******************** Helper Functions *****************
def extractDataFromRequest(request, key):
  # Returns the value of the key
  if request.GET.has_key(key):
    strValue = request.GET.get(key)
    try:
      value = int(strValue)
    except:
      try:
        value = float(strValue)
      except:
        value = strValue
    return value
  else:
    return None

def createCommandDict(request):
  # Creates a dictionary from the fields in the request
  # that constitute the JSON structure sent in the command
  # from AJAX.
  # Input: request - HTML request object
  # Output: result - dictionary of the command
  result = {}
  result['command'] = extractDataFromRequest(request, 'command')
  result['target'] = extractDataFromRequest(request, 'target')
  result['table_name'] = extractDataFromRequest(request, 'table')
  result['column_index'] = extractDataFromRequest(request, 'column')
  row_name = extractDataFromRequest(request, 'row')
  try:
    do_conversion = isinstance(int(row_name), int)
  except:
    do_conversion = False
  if do_conversion:
    result['row_index'] = UITable.rowIndexFromName(row_name)
  result['value'] = extractDataFromRequest(request, 'value')
  return result

def unPickleTable(request):
  # Returns the table if found
  if request.session.has_key(PICKLE_KEY):
    pickle_file = request.session.get(PICKLE_KEY)
    if not os.path.isfile(pickle_file):
      return None
    else:   
      return pickle.load( open(pickle_file, "rb"))
  else:
    return None

def pickleTable(request, table):
  if not request.session.has_key(PICKLE_KEY):
    fh = tempfile.NamedTemporaryFile()
    request.session[PICKLE_KEY] = fh.name  # Just get the name
    fh.close()
  pickle_file = request.session.get(PICKLE_KEY)
  pickle.dump(table, open(pickle_file, "wb"))


# ******************** Command Processing *****************

def scisheets(request, ncol, nrow):
  # Creates a new table with the specified number of columns and rows
  table = UITable.createRandomIntTable("Demo", ncol, nrow)
  html = table.render()
  pickleTable(request, table)
  return HttpResponse(html)

def scisheets_command(request, _, __):
  # Handles case where command is invoked with arguments
  return scisheets_command0(request)

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
    html = table.render()
  return HttpResponse(html)

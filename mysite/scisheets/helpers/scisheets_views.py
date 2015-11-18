'''The file handles the logic of the views'''

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from ..ui.ui_table import makeJSONStr, getContext
from ..core.column import Column
from ..ui.ui_table import UITable
import json
import numpy as np
import os
import pickle
import tempfile

PICKLE_KEY = "pickle_file"


# ******************** Helper Functions *****************
def extractDataFromGet(request, key):
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
  pickle_file = request.session[PICKLE_KEY]
  pickle.dump(table, open(pickle_file, "wb"))


# ******************** Command Processing *****************

def scisheets(request, ncol, nrow):
  # Creates a new table with the specified number of columns and rows
  table = UITable("DemoTable")
  for c in range(int(ncol)):
    column = Column("Col-" + str(c))
    values = np.random.randint(1, 100, int(nrow))
    column.addCells(values)
    table.addColumn(column)
  html = table.render()
  pickleTable(request, table)
  return HttpResponse(html)

def scisheets_command(request, _, __):
  # Handles case where command is invoked with arguments
  return scisheets_command0(request)

def scisheets_command0(request):
  # Invoked from Ajax within the page with a command structure
  # Input: request - includes command structure in the GET
  # Output returned: ???
  command = extractDataFromGet(request, 'command')
  table = extractDataFromGet(request, 'table')
  column_index = extractDataFromGet(request, 'column')
  if column_index is not None:
    column_index -= 1  # Adjust for 0 based indexing
  row_name = extractDataFromGet(request, 'row')
  value = extractDataFromGet(request, 'value')
  table = unPickleTable(request)
  if command == "Update":
    row_index = table.rowIndexFromName(row_name)
    table.updateCell(value, row_index, column_index)
  else:
    NotYetImplemented
  pickleTable(request, table)
  data = {'data': "OK", 'success': True}
  json_str = json.dumps(data)
  return HttpResponse(json_str, content_type="application/json")

def scisheets_reload(request):
  # Invoked to reload the current page
  table = unPickleTable(request)
  if table is None:
    html = "No session found"
  else:
    html = table.render()
  return HttpResponse(html)

'''The file handles the logic of the views'''

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from ..ui.ui_table import makeJSONStr, getContext
from ..core.column import Column
from ..ui.ui_table import UITable
import numpy as np
import pickle

PICKLE_FILE = "pickle.p"
PICKLE_KEY = "pickle_file"


def scisheets(request, ncol, nrow):
  # Creates a new table with the specified number of columns and rows
  table = UITable("DemoTable")
  for c in range(int(ncol)):
    column = Column("Col-" + str(c))
    values = np.random.randint(1, 100, int(nrow))
    column.addCells(values)
    table.addColumn(column)
  request.session[PICKLE_KEY] = PICKLE_FILE
  pickle.dump(table, open(PICKLE_FILE, "wb"))
  html = table.render()
  return HttpResponse(html)

def scisheets_reload(request):
  # Invoked to reload the current page
  if request.session.has_key(PICKLE_KEY):
    table = pickle.load( open(request.session[PICKLE_KEY], "rb"))
    html = table.render()
  else:
    html = "No session found"
  return HttpResponse(html)

def scisheets_command(request):
  # Invoked from Ajax within the page
  # Input: ???
  # Output returned: ???
  NotYetImplemented

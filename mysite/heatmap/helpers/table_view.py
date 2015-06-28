'''Trying a table view'''

from mysite.helpers.db_access import (DBAccess, CUR_DB)
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from mysite.helpers import file_access as fa
from mysite import settings
from mysite.helpers.file_to_db import FileTable
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime
import json
import os


NUM_ROWS = 10

#######################
# Forms
#######################

class TableForm(forms.Form):
    numrows = forms.IntegerField(label="Rows displayed",
        initial=NUM_ROWS, required=False)
    lastrow = forms.IntegerField(widget=forms.HiddenInput(),
        initial=0, required=False)

class QueryForm(forms.Form):
  query_string = forms.CharField(label="SQL Query", max_length=255,
      required=False)


#############################
# Exceptions
#############################
class Error(Exception):
  """Base class for exceptions."""

class TableviewUserError(Error):
  def __init__(self, msg):
    self.msg = msg

class TableviewInternalError(Error):
  def __init__(self, msg):
    self.msg = msg


#############################
# Helper Functions
#############################
def GetFieldFromForm(form, field):
  # This function extracts fields from a form
  # This takes into account an oddity in the django test framework
  # in which POST data is not properly setup.
  # The function assumes that is_valid() has already been invoked for the form.
  # Input: form - instance of form to be processed
  #        field - field to be retrieved
  # Output: field value
    value = form.cleaned_data[field]
    if value is None:  # This is because is_valid() doesn't work right for test
      value = form.fields[field].initial
    return value


#######################
# Main Functions
#######################

# To set up choices for tables, use ModelMultipleChoiceField
# which is the result of a queryset
def maketable(request):
  table_list = FileTable.DataTableList(CUR_DB)
  if request.method == 'POST':
    tablename = request.POST['tablename']
    table_list.remove(tablename)
    table_list.insert(0, tablename)  # Make sure it's the default
    # Create a form instance and populate it with data from the request:
    display_form = TableForm(request.POST)
    # check whether it's valid:
    if display_form.is_valid():
      numrows = GetFieldFromForm(display_form, 'numrows')
      lastrow = GetFieldFromForm(display_form, 'lastrow')
      dba = DBAccess()
      if not dba.IsTablePresent(tablename): 
        raise TableviewUserError("Cannot find table %s" % tablename)
      headers = dba.GetSchema(tablename)
      sql_str = 'SELECT * FROM %s' % tablename 
      all_rows, _ = dba.ExecuteQuery(sql_str)
      if 'Next' in request.POST:
        firstrow = lastrow + 1
      else:
        firstrow = lastrow - 2*numrows
      lastrow = firstrow + numrows - 1
      rows = all_rows[firstrow-1:lastrow-1]
      new_display_form = TableForm(initial={
          'numrows': numrows, 'lastrow': lastrow})
      ctx_dict = {'rows':rows, 
          'display_form': new_display_form, 
          'tablename': tablename,
          'headers': headers,
          'table_list': table_list,
          }
      return render_to_response('table_view.html', ctx_dict, 
          context_instance=RequestContext(request))
    else:
      pass

  # if a GET (or any other method) we'll create a blank form
  else:
    display_form = TableForm()

  return render(request, 'table_request.html', 
      {'display_form': display_form,
       'table_list': table_list})

# Deletes a table
def deletetable(request):
  if request.method == 'POST':
    tablename = request.POST['tablename']
    FileTable.RemoveUploadedFile(tablename)
    message = "Successfully removed table %s!" % tablename
    ctx = Context({'message': message})
    html = get_template('confirmation.html').render(ctx)
    return HttpResponse(html)

  # if a GET (or any other method) we'll create a blank form
  else:
    table_list = FileTable.DataTableList(CUR_DB)
    return render(request, 'delete_table.html', {'table_list': table_list})

# Execute a query.
def query(request):
  dba = DBAccess()
  if request.method == 'POST':
    # Create a form instance and populate it with data from the request:
    query_form = QueryForm(request.POST)
    # check whether it's valid:
    if query_form.is_valid():
      query_string = GetFieldFromForm(query_form, 'query_string')
      if len(query_string) > 0:
        rows,_ = dba.ExecuteQuery(query_string)
        headers = dba.GetSchemaFromSelect(query_string)
        if len(rows[0]) != len(headers):
          raise TableviewInternalError("header length doesn't match row length")
      else:  # Used in test
        rows = []
        headers = []
      ctx_dict = {'rows':rows, 
          'query_string': query_string,
          'headers': headers,
          }
      return render_to_response('query_result.html', ctx_dict, 
          context_instance=RequestContext(request))
    else:
      pass

  # if a GET (or any other method) we'll create a blank form
  # Extend by including the schemas with types
  else:
    query_form = QueryForm()
  table_list = FileTable.DataTableList(CUR_DB)
  rows = []
  dba = DBAccess()
  for table in table_list:
    row = [table, ", ".join(dba.GetSchema(table))]
    rows.append(row)
  return render(request, 'query_request.html', 
      {'rows': rows,
       'query_form': query_form,
      })

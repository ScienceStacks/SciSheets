'''The file handles the logic of the views'''

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from mysite import settings
from mysite.helpers import file_access as fa
from mysite.helpers.csv_formatter import GeneticCodeAsNestedDict
from mysite.helpers.db_access import (DBAccess, CUR_DB)
from mysite.helpers.file_to_db import FileTable
import datetime
import json
import os

#######################
# Forms
#######################

class UploadFileForm(forms.Form):
    filename = forms.FileField()

class NameForm(forms.Form):
    filename = forms.CharField(label='file', max_length=100)
    keyvariable = forms.CharField(label='key_variable', max_length=100)


#######################
# View Helpers
#######################

def letter(request):
  now = datetime.datetime.now()
  t = get_template('test_template.html')
  html = t.render(Context({'person_name': 'John', 'current_date': now}))
  return HttpResponse(html)

def plot(request, filename):
  # Input: filename - file in uploads to plot
  # Output: html for page for the data to plot
  file_path = os.path.join(settings.UPLOAD_DIR, filename)
  c2j = fa.CrdFile2Json(file_path)
  c2j.ReadAll()
  xcrds = c2j.GetXCrds()
  ycrds = c2j.GetYCrds()
  points = c2j.GetPoints()
  headers = c2j.GetHeaders()
  ctx = Context({
      'data': points, 
      'xcrds': xcrds, 
      'ycrds': ycrds,
      'xlabel': headers[1],
      'ylabel': headers[0],
      'values': headers[2],
      })
  t_heatmap = get_template('heatmap.html')
  html = t_heatmap.render(ctx)
  return HttpResponse(html)

def upload(request):
  # Handles requests to upload a file
  # if this is a POST request we need to process the form data
  if request.method == 'POST':
    # Create a form instance and populate it with data from the request:
    form = UploadFileForm(request.POST, request.FILES)
    # check whether it's valid:
    if form.is_valid():
      f = request.FILES['filename']
      name = str(f)
      process_uploaded_file(f, name)
      table_name, _ = fa.SplitFilename(name)
      message = "Success uploading file %s. Data are in table %s. " % (
          name, table_name)
      ctx = Context({'message': message})
      html = get_template('confirmation.html').render(ctx)
      return HttpResponse(html)

  # if a GET (or any other method) we'll create a blank form
  else:
    form = UploadFileForm()
  return render(request, 'upload.html', 
     {'form': form, 
     })

def codons(request):
  # To generalize so that cells can be merged and hence multiple
  # values may be present, construct a string from the vectorss.
  t_codons = get_template('codons.html')
  data_dict = GeneticCodeAsNestedDict()[0]
  NUCLEOTIDES = ['A', 'C', 'G', 'T']
  ctx_dict = {}
  #for nuc in NUCLEOTIDES:
  for n in range(len(NUCLEOTIDES)):
    nuc = NUCLEOTIDES[n]
    cur_var = "data_%d" % n
    json_var = "json_%s" % cur_var
    exec("%s = data_dict[nuc]" % cur_var)
    exec("%s = json.dumps(%s)" % (json_var, cur_var)) 
    exec("ctx_dict['%s'] = %s" % (json_var, json_var))
  ctx_dict["top_header"] = NUCLEOTIDES
  ctx = Context(ctx_dict)
  html = t_codons.render(ctx)
  return HttpResponse(html)

def nested(request):
  t_nested_tables = get_template('nested_tables.html')
  html = t_nested_tables.render({})
  return HttpResponse(html)

def tables(request, node):
  # To generalize so that cells can be merged and hence multiple
  value = request.GET.getlist('value', '')
  html = "Node is %s. Selection is %s" % (node, value)
  return HttpResponse(html)

#################################
# Auxiliary functions
#################################
def process_uploaded_file(f, name):
  partial_path = "mysite/uploads/%s" % name
  uploaded_file = os.path.join(settings.BASE_DIR, partial_path)
  with open(uploaded_file, 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)
  ft = FileTable(uploaded_file)
  ft.CreateAndPopulateTable()

from django import forms
from django.http import HttpResponse
from heatmap.helpers import helpers_views as hv
from heatmap.helpers import table_view as tv


#######################
# Request handlers
#######################
def hello(request):
  return HttpResponse("Hello world")

def letter(request):
  return hv.letter(request)

# EXTRACT THE FILE FROM THE URL
def plot(request, filename):
  file_path = 'mysite/static/data_rev.tsv'
  return hv.plot(request, filename)

def upload(request):
  return hv.upload(request)

def maketable(request):
  return tv.maketable(request)

def deletetable(request):
  return tv.deletetable(request)

def query(request):
  return tv.query(request)

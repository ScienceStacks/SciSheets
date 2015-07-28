from django import forms
from django.http import HttpResponse
from scisheets.helpers import helpers_views as hv
from scisheets.helpers import html_tables_views as ht
from heatmap.helpers import table_view as tv


#######################
# Request handlers
#######################
def hello(request):
  return HttpResponse("Hello world")

def letter(request):
  return hv.letter(request)

def plot(request, filename):
  return hv.plot(request, filename)

def upload(request):
  return hv.upload(request)

def maketable(request):
  return tv.maketable(request)

def deletetable(request):
  return tv.deletetable(request)

def query(request):
  return tv.query(request)

def codons(request):
  return hv.codons(request)

def nested(request):
  return hv.nested(request)

def tables(request, node):
  return hv.tables(request, node)

def simple_html_tables(request):
  return ht.SimpleHTMLTables(request)

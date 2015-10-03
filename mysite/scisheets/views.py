from django import forms
from django.http import HttpResponse
from scisheets.helpers import helpers_views as hv
from scisheets.helpers import html_tables_views as ht
from scisheets.helpers import scisheets_views as sv
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

def scisheets(request):
  return sv.scisheets(request)

''' Handle requests for images from jquery-ui
/*
 def images(request, filename):
 create a file attachment. modify the header. use response.write
   file_path = "./mysite/template/jquery-ui/image" + filename
   return render_to_response(file_path, { 'img':
*/
'''

from django import forms
from django.http import HttpResponse
from scisheets.helpers import helpers_views as hv
from scisheets.helpers import scisheets_views as sv
from heatmap.helpers import table_view as tv
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json


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

def scisheets(request, ncol, nrow):
  return sv.scisheets(request, ncol, nrow)

def scisheets_reload(request):
  return sv.scisheets_reload(request)

def tryajax(request):
  html = get_template('tryajax.html').render({})
  return HttpResponse(html)

def tryajax_reply(request):
  if request.GET.has_key('column'):
    val = int(request.GET.get('column'))
    if val < 1:
       msg = "<1"
    else:
       msg = ">=1"
    data = {'data': msg, 'success': True}
    json_str = json.dumps(data)
    return HttpResponse(json_str, content_type="application/json")
  return HttpResponse('got reply')

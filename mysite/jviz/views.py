from django import forms
from django.http import HttpResponse
from jviz.helpers import helpers_views as hv


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

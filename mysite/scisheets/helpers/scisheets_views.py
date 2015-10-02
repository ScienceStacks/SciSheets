'''The file handles the logic of the views'''

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from mysite import settings
from mysite.helpers.db_access import (DBAccess, CUR_DB)
import datetime
import json
import os

def scisheets(request):
  html = get_template('scitable.html').render({})
  return HttpResponse(html)

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

# This version uses templates to generate column names
def scisheets(request):
  column_names = ["row", "name", "address", "salary"]
  initial_column_names = column_names[0:-1]
  final_column_name = column_names[-1]
  table_id = "cellediting"
  table_caption = "New table"
  ctx_dict = {'column_names': column_names,
              'initial_column_names': initial_column_names,
              'final_column_name': final_column_name,
              'table_id': table_id,
              'table_caption': table_caption,
             }
  html = get_template('scitable.html').render(ctx_dict)
  return HttpResponse(html)

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
  final_column_name = column_names[-1]
  table_id = "cellediting"
  table_caption = "Demo Table"
  data = []
  data.append(["1", "John A. Smith", "1236 Some Street", "12.33"])
  data.append(["2", "Joan B. Jones", "3271 Another Ave", "34556"])
  data.append(["3", "Bob C. Uncle", "9996 Random Road", "893"])
  data_dic = {}
  for r in range(len(data)):
    for c in range(len(column_names)):
      data_dic[column_names[c]] = data[r][c] 
  ctx_dict = {'column_names': column_names,
              'final_column_name': final_column_name,
              'table_id': table_id,
              'table_caption': table_caption,
              'data_dic': data_dic,
              'data': data,
              'final_data': data[-1],
             }
  html = get_template('scitable.html').render(ctx_dict)
  return HttpResponse(html)

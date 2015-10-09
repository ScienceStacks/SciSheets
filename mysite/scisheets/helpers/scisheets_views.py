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

ROW_COLUMN_NAME = "row"
MIN_NUM_ROWS = 5

def Make_JSON_string(column_names, data):
  # Creates a string that javascript parses into JSON
  # Input: column_names - list of names of the data columns
  #        data - list of columns of data
  # Output: result - JSON parseable string
  # Note: the "row" column is added automatically
  # Augment the names and data with "row"
  column_names.insert(0, ROW_COLUMN_NAME)
  number_of_columns = len(column_names)
  number_of_rows = MIN_NUM_ROWS
  if len(data) > 0:
    number_of_rows = max(MIN_NUM_ROWS, len(data[0]))
  rows = range(1, number_of_rows + 1)
  data.insert(0, rows)
  result = "'["
  for r in range(number_of_rows):
    result += "{"
    for c in range(number_of_columns):
      result += ('"' + column_names[c] + '": ' + 
          '"' + str(data[c][r]) + '"')
      if c != number_of_columns - 1:
        result += ","
      else:
        result += "}"
    if r < number_of_rows -1:
      result += ","
    else:
      result += "]'"
  return result
      

# This version uses templates to generate column names
def scisheets(request):
  column_names = ["row", "name", "address", "salary"]
  final_column_name = column_names[-1]
  table_id = "cellediting"
  table_caption = "Demo Table"
  names = ["John A. Smith", "Joan B. Jones", "Bob C. Uncle", "John D. Smith", "Joan E. Jones"]
  addresses = ["1236 Some Street", "3271 Another Ave", "9996 Random Road", "1623 Some Street", "3217 Another Ave"]
  salaries = ["12.33", "34556", "893", "0.092", "23456"]
  data = Make_JSON_string(column_names[1:], 
      [names, addresses, salaries])
  ctx_dict = {'column_names': column_names,
              'final_column_name': final_column_name,
              'table_id': table_id,
              'table_caption': table_caption,
              'data': data,
             }
  html = get_template('scitable.html').render(ctx_dict)
  return HttpResponse(html)

'''The file handles the logic of the views'''

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from ..ui.ui_table import makeJSONStr, getContext, makeColumnSpec
from ..core.column import Column


# This version uses templates to generate column names
def scisheets(request):
  column_names = ["row", "name", "address", "salary"]
  final_column_name = column_names[-1]
  table_id = "scitable" # Must match ID in the html file
  table_caption = "Demo Table"
  names = ["John Q. Smith", "Joan B. Jones", "Bob C. Uncle", "John D. Smith", "Joan E. Jones", "Jacob Burns"]
  addresses = ["1236 Some Street", "3271 Another Ave", "9996 Random Road", "1623 Some Street", "3217 Another Ave", "7118 McGee"]
  salaries = ["12.33", "34556", "893", "0.092", "23456", "20,101"]
  row_names = [str(n+1) for n in range(len(names))]
  data = makeJSONStr(column_names, 
      [row_names, names, addresses, salaries])
  ctx_dict = {'column_names': column_names,
              'final_column_name': final_column_name,
              'table_caption': table_caption,
              'table_id': table_id,
              'data': data,
             }
  html = get_template('scitable.html').render(ctx_dict)
  return HttpResponse(html)

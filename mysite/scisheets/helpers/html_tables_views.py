'''The file handles the logic of HTMLTables pages.'''

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from mysite import settings
from mysite.helpers import file_access as fa
from mysite.helpers.csv_formatter import GeneticCodeAsNestedDict
from mysite.helpers.db_access import (DBAccess, CUR_DB)
from mysite.helpers.file_to_db import FileTable
import datetime
import json
import os

#######################
# Forms
#######################

class UploadFileForm(forms.Form):
    filename = forms.FileField()

class NameForm(forms.Form):
    filename = forms.CharField(label='file', max_length=100)
    keyvariable = forms.CharField(label='key_variable', max_length=100)


#######################
# View Helpers
#######################

def test_html_tables(request):
  return HttpResponse("Not implemented")

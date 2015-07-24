'''Models used in applications.'''
from django.db import models

MAX_CHAR = 100

class UploadedFiles(models.Model):
  file_name = models.CharField(max_length=MAX_CHAR, 
      primary_key=True)  # Name of file with extension
  file_path = models.CharField(max_length=MAX_CHAR)  # Containing directory
  table_name = models.CharField(max_length=MAX_CHAR) # Name of table in DB

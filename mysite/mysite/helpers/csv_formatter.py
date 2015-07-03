'''Formats CSV files'''

from mysite import settings
import csv
import json
import os


#############################
# Exceptions
#############################
class Error(Exception):
  """Base class for exceptions."""

class FileError(Error):
  def __init__(self, msg):
    self.msg = msg

class InternalError(Error):
  def __init__(self, msg):
    self.msg = msg


#############################
# Functions
#############################
import csv
def GeneticCodeAsDict():
  # Converts a CSV file of codons to a nested dictionary
  # Output: result - dictionary representation of codons
  #         in which the keys are single nucleotides at 3 levels
  FILE = os.path.join(settings.BASE_DIR, 'mysite/helpers/codons.csv')
  with open(FILE) as csvfile:
    reader = csv.DictReader(csvfile)
    result = {}
    for row in reader:
      result[row['CODON']] = row['AA']
    return result

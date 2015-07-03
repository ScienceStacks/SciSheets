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

def GeneticCodeAsNestedDict():
  # Constructs a tested dictionary representation of 
  # as a nested dictionary
  aa_by_codon = GeneticCodeAsDict()
  NUCLEOTIDES = ['A', 'C', 'G', 'T']
  entry1 = {}
  for c1 in NUCLEOTIDES:
    entry2 = {}
    for c2 in NUCLEOTIDES:
      entry3 = {}
      for c3 in NUCLEOTIDES:
        codon = "%s%s%s" % (c1, c2, c3)
        entry3[c3] = aa_by_codon[codon]
      entry2[c2] = [ entry3 ]
    entry1[c1] = [ entry2 ]
  return [ entry1 ]

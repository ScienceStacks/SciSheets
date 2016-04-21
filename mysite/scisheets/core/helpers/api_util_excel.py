"""
Wrappers for reading and writing excel files
"""

import cell_types
import collections
import numpy as np
import openpyxl
import os

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUM_LETTERS = len(LETTERS)


################### CLASSES ######################
class APIUtilExcel(object):
  """
  Class that manages interactions with excel xlsx files
  """

  def __init__(self, filepath):
  """
  :param str filepath: path to the excel file
  """
    self._filepath = filepath
    self._wb = None  # Not initialize

  def initialize(self):
  """
  Initializes connection with excel file
  :return str error:
  """
  error = None
  try:
    self._wb = load_workbook(filename=self._filepath, 
                             read_only=True)
  except IOError as err:
    error = str(err)
  return error

  def _calcColumnIndexFromLetters(self, letters):
    """
    Calculate the column index from one or more letters given.
    :param str letters:
    :return int:
    """
    letter_list = list(letters)
    letter_list.reverse()  # Low to high order letters
    index = 0
    factor = 1
    for letter in letter_list:
      index +=  factor*(LETTERS.index(letter) + 1)
      factor = factor*NUM_LETTERS
    return index

  def _getColumnFromWorksheet(self, worksheet, index):
    """
    :param str worksheet:
    :param int index: 1-based index of the column
    :returns list:
    """
    ws = wb[worksheet]
    result = []
    for row in ws.rows:
      for cell in row:
        if cell.column == index:
          result.append(cell.value)
    return result

  def getColumnValues(self, column_letters, worksheet=None, header=False):
    """
    Reads the column in the specified worksheet. If no worksheet
    is specified, then the first one is read.
    :param str column_letters: Spreadsheet column read
    :param str worksheet: worksheet to read
    :param bool header: True if there is a header for the column
    :return np.array, str: column_values, header_value (if True)
    :raises ValueError:
    """
    sheets = wb.get_sheet_names()
    if worksheet is None:
      worksheet = sheets[0]
    if not worksheet in sheets:
      error = "Worksheet %s not found in %s"  \
          % (worksheet, self._filepath)
      raise ValueError(error)
    index = self._calcColumnIndexFromLetters(column_letters)
    values = self._getColumnFromWorksheet(worksheet, index):
    if header:
      header = values[0]
      del values[0]
    else:
      header = None
    return np.array(values), header

"""
Imports an Excel file and adds it to the table
"""

import pandas as pd

def importExcelToDataframe(filepath, worksheet=None):
  """
  Reads the excel file into a dataframe.
  :param str filepath: full path to CSV file
  :param str worksheet: worksheet to import. Default is first.
  :raises IOError, ValueError:
  """
  xls_file = pd.ExcelFile(filepath)  # May raise IOError
  if worksheet is None:
    worksheet = xls_file.sheet_names[0]
  if worksheet not in xls_file.sheet_names:
    raise ValueError("Worksheet %s not found in file %s"  \
        % (worksheet, filepath))
  return xls_file.parse(worksheet)

def importExcel(s, filepath, worksheet=None, names=None):
  """
  Imports the specified columns from the excel file.
  Columns that don't exist in the current table are created.
  :param API s: API object
  :param str filepath: full path to CSV file
  :param str worksheet: worksheet to import. Default is first.
  :param list-of-str names: names of columns added
  :return list-of-str: column names imported
  """
  df = importExcelToDataframe(filepath, worksheet=worksheet)
  imported_names = s.addColumnsToTableFromDataframe(df, names=names)
  s.updateTableFile()
  return imported_names

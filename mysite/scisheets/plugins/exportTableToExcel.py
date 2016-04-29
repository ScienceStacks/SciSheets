"""
Exports an Excel file 
"""

import pandas as pd

def _exportDataframeToExcel(df, filepath, worksheet=None):
  """
  Export the specified columns to the excel file.
  The existing worksheet is overwritten.
  :param str filepath: full path to CSV file
  :param pandas.DataFrame df:
  :param str worksheet: worksheet to import. Default is first.
  :raises IOError, ValueError:
  """
  if worksheet is None:
    worksheet = 'Sheet1'
  writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
  df.to_excel(writer, sheet_name=worksheet)
  writer.save()

def exportTableToExcel(s, filepath, worksheet=None, names=None):
  """
  Export the specified columns of the Table to the excel file.
  The existing worksheet is overwritten.
  :param API s:
  :param str filepath: full path to CSV file
  :param str worksheet: worksheet to import. Default is first.
  :param list-of-str names: names of columns added
  :raises ValueError:
  """
  df = s.tableToDataframe(names=names)
  _exportDataframeToExcel(df, filepath, worksheet=worksheet)

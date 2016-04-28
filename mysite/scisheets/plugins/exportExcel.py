"""
Exports an Excel file 
"""

import pandas as pd

def exportDataframeToExcel(filepath, df, worksheet=None, names=None):
  """
  Export the specified columns to the excel file.
  The existing worksheet is overwritten.
  :param pandas.DataFrame df:
  :param str filepath: full path to CSV file
  :param str worksheet: worksheet to import. Default is first.
  :param list-of-str names: names of columns added
  :raises IOError, ValueError:
  """
  if names is None:
    names = df.columns
  if worksheet is None:
    worksheet = 'Sheet1'
  new_df = DataFrame()
  for name in names:
    new_df[name] = df[name]
  writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
  new_df.to_excel(writer, sheet_name=worksheet)
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
  exportDataframeToExcel(filepath, df, worksheet=worksheet, names=names)

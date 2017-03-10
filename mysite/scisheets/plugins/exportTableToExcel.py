"""
Exports an Excel file 
"""

import openpyxl
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
  book = openpyxl.load_workbook(filepath)
  # Delete the sheet to write, if it exists
  if worksheet in book.get_sheet_names():
    ws = book.get_sheet_by_name(worksheet)
    book.remove_sheet(ws)
  writer = pd.ExcelWriter(filepath, engine='openpyxl')
  writer.book = book
  writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
  df.to_excel(writer, worksheet, index=False)
  writer.save()

#TODO: Eliminate column_name since have an ExtendedArray
def exportTableToExcel(s, filepath, worksheet=None, columns=None):
  """
  Export the specified columns of the Table to the excel file.
  The existing worksheet is overwritten.
  :param API s:
  :param str filepath: full path to CSV file
  :param str worksheet: worksheet to import. Default is first.
  :param list-of-str columns: columns of columns added
  :raises ValueError:
  """
  df = s.tableToDataframe(colnms=columns)
  _exportDataframeToExcel(df, filepath, worksheet=worksheet)

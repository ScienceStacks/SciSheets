"""
Imports an Excel file and adds it to the table
"""

import pandas as pd
import unicodedata

def _importExcelToDataframe(filepath, worksheet=None):
  """
  Reads the excel file into a dataframe.
  :param str filepath: full path to CSV file
  :param str worksheet: worksheet to import. Default is first.
  :return pandas.DataFrame:
  :raises IOError, ValueError:
  """
  xls_file = pd.ExcelFile(filepath)  # May raise IOError
  if worksheet is None:
    worksheet = xls_file.sheet_names[0]
  if not worksheet in xls_file.sheet_names:
    raise ValueError("Worksheet %s not found in file %s"  \
        % (worksheet, filepath))
  df = xls_file.parse(worksheet)
  # Make sure that column names are strings
  names = []
  for col in df.columns:
    name = unicodedata.normalize('NFC', col).encode('ascii', 'ignore')
    name = name.replace(' ', '')
    names.append(str(name))
  df.columns = names
  return df

def importExcelToTable(s, filepath, worksheet=None, names=None):
  """
  Imports the specified columns from the excel file.
  Columns that don't exist in the current table are created.
  :param API s: API object
  :param str filepath: full path to CSV file
  :param str worksheet: worksheet to import. Default is first.
  :param list-of-str names: names of columns added
  :return list-of-str: column names imported
  """
  df = _importExcelToDataframe(filepath, worksheet=worksheet)
  imported_names = s.addColumnsToTableFromDataframe(df, names=names)
  try:
    s.updateTableFile()
  except Exception as err:
    # TODO: Find out cause of unicode error
    if not 'coercing to Unicode' in err.message:
      import pdb; pdb.set_trace()
      raise ValueError(str(err))
  return imported_names

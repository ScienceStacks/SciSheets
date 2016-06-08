"""
Imports a CSV file and adds it to the table
"""

import pandas as pd

def importCSV(s, filepath, names=None):
  """
  Imports the specified columns from the csv file.
  Columns that don't exist in the current table are created.
  :param API s: API object
  :param str filepath: full path to CSV file
  :param list-of-str names: names of columns added
  :return list-of-str: column names imported
  :raises IOError:
  """
  df = pd.read_csv(filepath)  # May raise IOError
  imported_names = s.addColumnsToTableFromDataframe(df, names=names)
  return imported_names

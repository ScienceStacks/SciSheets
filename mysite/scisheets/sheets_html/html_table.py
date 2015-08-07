'''
  Extends the Table class to visualize (recursively) in HTML.
'''


from mysite.scisheets.sheets_core.table import Table
from numpy import array
from helpers import OrderableStrings


class HTMLTable(Table):

  def toHTML(self):
    # Returns HTML for the table
    headers = []
    # for columns in Table
    #  add column.name to headers
    rows = []
    # for row in Table
      row = []
    #   for column in Table
    #     row.append(column.to_hmtl(i)) 
    pass

'''Command Dictionary representation of Requests.'''

from django.http import HttpResponse
from scisheets.ui.dt_table import DTTable
import mysite.helpers.util as ut


# ******************** Helper Functions and Classes *****************
def _extractDataFromRequest(request, key, convert=False, listvar=False):
  """
  Returns the value of the key
  """
  if request.GET.has_key(key):
    if listvar:
      return request.GET.getlist(key)
    elif convert:
      return ut.ConvertType(request.GET.get(key))
    else:
      return request.GET.get(key)
  else:
    return None


class CommandDict(dict):
  """
  Container for the fields in the request
  that constitute the JSON structure sent in the command
  from AJAX.
  Input: request - HTML request object
  Output: cmd_dict - dictionary of the command
   TARGET  COMMAND   DESCRIPTION
    Sheet   Delete   Delete the sheet file and switch to the
                     using a random file
    Sheet   Export   Export the table into python
    Sheet   ListSheetFiles Returns a list of the table files
    Sheet   New      Opens a new blank table
    Sheet   OpenSheetFile Change the current Table file to
                     what is specified in the args list
    Sheet   Redo     Revert an undo
    Sheet   SaveAs   Save the sheet to the specified file file
    Sheet   UnhideAll Make all tables and columns visible
    Sheet   Undo     Revert to previous version
    Table   Delete   Delete the table
    Table   Epilogue Update the epilogue code for the table
    Table   Hide     Hide the table
    Table   Move     Reposition the table
    Table   Prologue Update the prologue code for the table
    Table   Rename   Change the table name. Must be a valid python name
    Table   Tablize  Create a subtable that contains this table
    Table   Trim     Remove None rows from the end of the table
    Table   Unhide   Make all columns of the Table visible
    Column  Append   Add a new column to the right of the current
    Column  Hide     Hide the columns
    Column  Insert   Add a new column to the left of the current
    Column  Delete   Delete the column
    Column  Formula  Change the column's formula
    Column  Move     Move the column to another position
                       The name LAST is used for last column
    Column  Refactor Rename the column and change formulas to use
                     the new name
    Column  Rename   Rename the column
    Column  Tablize  Create a subtable that contains this column
    Column  Unhide   Unhide the column
    Row     Append   Add a new row after the current row
    Row     Insert   Add a new row before the current row
    Row     Move     Move the row to the specified position
    Cell    Update   Update the specified cell
  Handles the conversion from the HTML name to the python name
  for a column.
  """

  def __init__(self, request):
    if request is None:
      return
    self['command'] = _extractDataFromRequest(request, 'command')
    self['target'] = _extractDataFromRequest(request, 'target')
    self['table_name'] = _extractDataFromRequest(request, 'table')
    self['args'] = _extractDataFromRequest(request, 'args[]', listvar=True)
    if self['args'] is not None:
      python_name = DTTable.fromHTMLToPythonName(self['args'][0])
      self['args'][0] = python_name
    html_name = _extractDataFromRequest(request, 'columnName')
    python_name = DTTable.fromHTMLToPythonName(html_name)
    self['column_name'] = DTTable.fromHTMLToPythonName(python_name)
    row_name = _extractDataFromRequest(request, 'row')
    if row_name is not None and len(str(row_name)) > 0:
      self['row_index'] = DTTable.rowIndexFromName(row_name)
    else:
      self['row_index'] = None  # Handles case where "row" is absent
    self['value'] = _extractDataFromRequest(request, 'value',
        convert=True)
    if self['row_index'] == -1:
      raise InternalError("Invalid row_index: %d" % self['row_index'])

  @classmethod
  def createCommandDict(cls, a_dict):
    cmd_dict = CommandDict(None)
    for key in a_dict.keys():
      cmd_dict[key] = a_dict[key]
    return cmd_dict

  def getFirstArgument(self):
    """
    Extracts the first argument if it exists
    :return str/int/None:
    """
    argument = None
    if "args" in self:
      arguments = self["args"]
      if isinstance(arguments, list):
        if len(arguments) > 0:
          argument = arguments[0]
    return argument

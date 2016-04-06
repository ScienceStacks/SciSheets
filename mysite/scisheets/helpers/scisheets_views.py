'''The file handles the logic of the views'''

from django.http import HttpResponse
from ..core.errors import InternalError
from ..core.util.api_util import getTableFromFile, writeTableToFile
from ..ui.dt_table import DTTable
import mysite.helpers.util as ut
import mysite.settings as st
import json
import os
import tempfile

TABLE_FILE_KEY = "tablefile"
USE_LOCAL_FILE = True
LOCAL_FILE = "scisheet_table"
EMPTY_TABLE_FILE = "_empty_table"


# ******************** Helper Functions *****************
def extractDataFromRequest(request, key, convert=False, listvar=False):
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

def createCommandDict(request):
  """
  Creates a dictionary from the fields in the request
  that constitute the JSON structure sent in the command
  from AJAX.
  Input: request - HTML request object
  Output: cmd_dict - dictionary of the command
   TARGET  COMMAND   DESCRIPTION
    Table   Delete   Delete the table file and switch to the
                     using a random file
    Table   Export   Export the table into python
    Table   ListTableFiles Returns a list of the table files
    Table   New      Opens a new blank table
    Table   OpenTableFile Change the current Table file to
                     what is specified in the args list
    Table   Rename   Change the table name. Must be a valid python name
    Table   SaveAs   Save the table to the specified table file
    Table   Trim     Remove None rows from the end of the table
    Cell    Update   Update the specified cell
    Column  Append   Add a new column to the right of the current
    Column  Insert   Add a new column to the left of the current
    Column  Delete   Delete the column
    Column  Formula  Change the column's formula
    Column  Move     Move the column to another position
                       The name LAST is used for last column
    Column  Rename   Rename the column
    Row     Append   Add a new row after the current row
    Row     Insert   Add a new row before the current row
    Row     Move     Move the row to the specified position
  """
  cmd_dict = {}
  cmd_dict['command'] = extractDataFromRequest(request, 'command')
  cmd_dict['target'] = extractDataFromRequest(request, 'target')
  cmd_dict['table_name'] = extractDataFromRequest(request, 'table')
  cmd_dict['args'] = extractDataFromRequest(request, 'args[]', listvar=True)
  cmd_dict['column_index'] = extractDataFromRequest(request,
      'column', convert=True)
  row_name = extractDataFromRequest(request, 'row')
  if row_name is not None and len(str(row_name)) > 0:
    cmd_dict['row_index'] = DTTable.rowIndexFromName(row_name)
  else:
    cmd_dict['row_index'] = None  # Handles case where "row" is absent
  cmd_dict['value'] = extractDataFromRequest(request, 'value',
      convert=True)
  if cmd_dict['row_index'] == -1:
    raise InternalError("Invalid row_index: %d" % cmd_dict['row_index'])
  return cmd_dict

def _makeAjaxResponse(data, success):
  return {'data': data, 'success': success}

def _getFileNameWithoutExtension(file_path):
  """
  Input: file_path - full path to the file
  Output: file_name - just the name, without extension
  """
  if file_path is None:
    return None
  full_file_name = os.path.split(file_path)[1]
  pos = full_file_name.index(".")
  return full_file_name[:pos]

def _createTableFilepath(file_name):
  suffix = ""
  if not file_name[-3:] != ".pcl":
    suffix = ".pcl"
  table_file = "%s%s" % (file_name, suffix)
  return os.path.join(st.SCISHEETS_USER_TBLDIR, table_file)

def _setTableFilepath(request, 
                      table, 
                      file_name, 
                      verify=True,
                      fullpath=False):
  """
  Sets the file path in the session key
  :param request: request for the session
  :param Table table: Table object
  :param str file_name: name of file without extension
  :param bool verify: check for a valid filepath
  :param bool fullpath: name is a full path
  :return str: Table filepath
  """
  if fullpath:
    table_filepath = file_name
  else:
    table_filepath = _createTableFilepath(file_name)
  if verify:
    if not os.path.isfile(table_filepath):
      raise InternalError("Could not find Table file %s"
          % table_filepath)
  request.session[TABLE_FILE_KEY] = table_filepath
  if table is None:
    import pdb; pdb.set_trace()
  table.setFilepath(table_filepath)
  return table_filepath

def _getTableFilepath(request):
  """
  Sets the file path in the session key
  Input: request - request for the session
  Output: file path or None if not found
  """
  if TABLE_FILE_KEY in request.session:
    return request.session[TABLE_FILE_KEY]
  else:
    return None

def getTable(request):
  """
 Returns the table if found
  """
  table_file_path = _getTableFilepath(request)
  if table_file_path is None:
    return None
  else:
    return getTableFromFile(table_file_path)

def _createRandomFileName():
  handle = tempfile.NamedTemporaryFile()
  file_name = os.path.split(handle.name)[1]
  handle.close()
  return file_name

def saveTable(request, table):
  """
  Serialize the table into its file
  :param request: HTTP request
  :param Table table:
  """
  have_table_file = False
  table_filepath = None
  if TABLE_FILE_KEY in request.session:
    if request.session[TABLE_FILE_KEY] is not None:
      have_table_file = True
      table_filepath = request.session[TABLE_FILE_KEY]
  if not have_table_file:
    if USE_LOCAL_FILE:
      table_filepath = LOCAL_FILE
    else:
      handle = tempfile.NamedTemporaryFile()
      table_filepath = handle.name
      handle.close()
  _setTableFilepath(request, table, table_filepath)
  writeTableToFile(table)


# ******************** Command Processing *****************
def scisheets(request, ncol, nrow):
  """
  Creates a new table with the specified number of columns and rows
  considering the number of rows with strings
  """
  ncol = int(ncol)
  nrow = int(nrow)
  ncolstr = int(ncol/2)
  table = DTTable.createRandomTable("Demo", nrow, ncol,
      ncolstr=ncolstr)
  _setTableFilepath(request, table, LOCAL_FILE, verify=False)
  table_file = table.getFilepath()
  html = table.render(table_file=table_file)
  saveTable(request, table)
  return HttpResponse(html)

def scisheets_command0(request):
  """
  Invoked from Ajax within the page with a command structure
  Input: request - includes command structure in the GET
  Output returned - HTTP response
  """
  cmd_dict = createCommandDict(request)
  command_result = _processUserEnvrionmentCommand(request, cmd_dict)
  if command_result is None:
    # Use table processing command
    table = getTable(request)
    command_result = table.processCommand(cmd_dict)
    saveTable(request, table)  # Save table modifications
  json_str = json.dumps(command_result)
  return HttpResponse(json_str, content_type="application/json")

def _makeNewTable(request):
  """
  Creates a new table
  :param request: includes command structure in the GET
  :return: ajax response
  """
  empty_table_file = _createTableFilepath(EMPTY_TABLE_FILE)
  table = getTableFromFile(empty_table_file)
  _setTableFilepath(request, table, LOCAL_FILE, verify=False)
  saveTable(request, table)  # Save table in the new path
  return _makeAjaxResponse("OK", True)

def _processUserEnvrionmentCommand(request, cmd_dict):
  """
  Processes commands that relate to the environment in which
  the user is executing.
  :param request: includes command structure in the GET
  :param cmd_dict: command informat extracted from the request
  :return: JSON structure or None if not a user environment command
  """
  command_result = None
  table = getTable(request)
  target = cmd_dict["target"]
  if target == 'Table':
    if cmd_dict['command'] == "Delete":
      current_file_path = _getTableFilepath(request)
      os.remove(current_file_path)
      command_result = _makeNewTable(request)
    elif cmd_dict['command'] == "ListTableFiles":
      command_result = _listTableFiles()
    elif cmd_dict['command'] == "New":
      command_result = _makeNewTable(request)
    elif cmd_dict['command'] == "OpenTableFile":
      filename = cmd_dict['args'][0]
      table_filepath = _createTableFilepath(filename)
      table = getTableFromFile(table_filepath, verify=False)
      _setTableFilepath(request, table, cmd_dict['args'][0])
      command_result = _makeAjaxResponse("OK", True)
    elif cmd_dict['command'] == "SaveAs":
      table = getTable(request)
      _setTableFilepath(request, table, cmd_dict['args'][0], 
          verify=False)
      saveTable(request, table)  # Save table in the new path
      command_result = _makeAjaxResponse("OK", True)
  return command_result

# TODO: Tests
def _listTableFiles():
  """
  Output: returns response that contains the list of table files in data
  """
  lensfx = len(".pcl")
  file_list = [ff[:-lensfx] for ff in os.listdir(st.SCISHEETS_USER_TBLDIR)
               if ff[-lensfx:] == '.pcl' and ff[0] != "_"]
  file_list.sort()
  return _makeAjaxResponse(file_list, True)

def scisheets_reload(request):
  """
  Invoked to reload the current page
  """
  table = getTable(request)
  if table is None:
    html = "No session found"
  else:
    table.evaluate()  # Saves the changes to the table in the Table File
    table_file = _getFileNameWithoutExtension(table.getFilepath())
    html = table.render(table_file=table_file)
  return HttpResponse(html)

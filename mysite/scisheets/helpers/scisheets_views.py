'''The file handles the logic of the views'''

from django.http import HttpResponse
from FileVersion.versioned_file import VersionedFile
from scisheets.core.errors import InternalError
from scisheets.core.helpers.api_util import readObjectFromFile, \
    writeObjectToFile, getFileNameWithoutExtension
from scisheets.ui.dt_table import DTTable
import CommonUtil.util as ut
from command_dict import CommandDict
import mysite.settings as settings
import json
import os
import tempfile

TABLE_FILE_KEY = "tablefile"
USE_DEFAULT_FILE = True
EMPTY_TABLE_FILE = "_empty_table"


############################################################
# Helper Functions
############################################################
def _makeAjaxResponse(data, success):
  return {'data': data, 'success': success}

def _createTableFilepath(file_name):
  """
  Input: file_name - name of file without extension
  Output: file_path - full path for file
  """
  path =  os.path.join(settings.SCISHEETS_USER_TBLDIR, file_name)
  adj_path = ut.changeFileExtension(path, settings.SCISHEETS_EXT)
  return adj_path

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
  if ut.getFileExtension(table_filepath) != settings.SCISHEETS_EXT:
    import pdb; pdb.set_trace()
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
    return readObjectFromFile(table_file_path, verify=False)

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
    if USE_DEFAULT_FILE:
      table_filepath = settings.SCISHEETS_DEFAULT_TABLEFILE
    else:
      handle = tempfile.NamedTemporaryFile()
      table_filepath = handle.name
      handle.close()
  full_filepath = _setTableFilepath(request, table, table_filepath, 
      verify=False)
  versioned_file = table.getVersionedFile()
  if versioned_file is None:
    is_changed_filepath = True
  elif full_filepath != versioned_file.getFilepath():
    is_changed_filepath = True
  else:
    is_changed_filepath = False
  if is_changed_filepath:
    table.setFilepath(full_filepath)
  writeObjectToFile(table)


################################################################
# Command Processing
################################################################
def scisheets(request, ncol, nrow):
  """
  Creates a new table with the specified number of columns and rows
  considering the number of rows with strings. 
  Renders a hierarchical table if ncol < 0.
  """
  ncol = int(ncol)
  nrow = int(nrow)
  ncolstr = int(ncol/2)
  if ncol < 0:  # Test for hierarchical table
    num_nodes = 2*abs(ncol)
    prob_child = 0.5
    table = DTTable.createRandomHierarchicalTable("HDemo", nrow,
      num_nodes, prob_child, prob_detach=0.5,
      ncolstr=ncolstr, table_cls=DTTable)
  else:
    table = DTTable.createRandomTable("Demo", nrow, ncol,
        ncolstr=ncolstr)
  _setTableFilepath(request, table, 
      settings.SCISHEETS_DEFAULT_TABLEFILE,
      verify=False)
  html = table.render()
  saveTable(request, table)
  return HttpResponse(html)

def scisheets_command0(request):
  """
  Invoked from Ajax within the page with a command structure
  Input: request - includes command structure in the GET
  Output returned - HTTP response
  """
  cmd_dict = CommandDict(request)
  command_result = _processUserEnvrionmentCommand(request, cmd_dict)
  if command_result is None:
    # Use table processing command
    table = getTable(request)
    command_result, do_save = table.processCommand(cmd_dict)
    if do_save:
      saveTable(request, table)
  json_str = json.dumps(command_result)
  return HttpResponse(json_str, content_type="application/json")

def _makeNewTable(request):
  """
  Creates a new table
  :param request: includes command structure in the GET
  :return: ajax response
  """
  empty_table_file = _createTableFilepath(EMPTY_TABLE_FILE)
  table = readObjectFromFile(empty_table_file)
  _setTableFilepath(request, table, 
      settings.SCISHEETS_DEFAULT_TABLEFILE,
      verify=False)
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
  if target == 'Sheet':
    if cmd_dict['command'] == "Delete":
      current_file_path = _getTableFilepath(request)
      os.remove(current_file_path)
      command_result = _makeNewTable(request)
    elif cmd_dict['command'] == "ListSheetFiles":
      command_result = _listTableFiles()
    elif cmd_dict['command'] == "New":
      command_result = _makeNewTable(request)
    elif cmd_dict['command'] == "OpenSheetFile":
      filename = cmd_dict['args'][0]
      table_filepath = _createTableFilepath(filename)
      table = readObjectFromFile(table_filepath, verify=False)
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
  file_list = [ut.stripFileExtension(ff)
               for ff in os.listdir(settings.SCISHEETS_USER_TBLDIR)
               if ut.getFileExtension(ff) == settings.SCISHEETS_EXT
                  and ff[0] != "_"]
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
    html = table.render()
  return HttpResponse(html)

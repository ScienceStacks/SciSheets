'''Utility routines that add in file access'''

from mysite.helpers import util as ut
import json


#############################
# Exceptions
#############################
class Error(Exception):
  """Base class for exceptions."""

class FileError(Error):
  def __init__(self, msg):
    self.msg = msg

class InternalError(Error):
  def __init__(self, msg):
    self.msg = msg


#############################
# Functions
#############################
def SplitFilename(filename):
  # Returns the name and extension
  # Input: filename - <file>.<ext>
  # Output: (file, ext)
  result = (filename, "")
  pos = filename.find(".")
  if pos >- 0:
    result = filename[0:pos], filename[pos+1:]
  return result


#############################
# Classes
#############################
class _FileBase(object):
  # Base class used in file accesses

  def __init__(self, filename):
    # Input: file name
    # Assumes that the first line are the variable names
    self._filename = filename
    self._OpenFile()
    self._colnames = self._fh.readline().split()  # Column names
    self._CloseFile()

  def _OpenFile(self):
    # Only _OpenFile and _CloseFile modify self._fh
    # On output, self._fh points to the fie
    try:
      self._fh = open(self._filename, 'r')
    except:
      raise FileError("%s cannot be opened" % self._filename)

  def _CloseFile(self):
    # Only _OpenFile and _CloseFile modify self._fh
    self._fh.close()
    self._fh = None
      

class File2Json(_FileBase):
  # Creates json string from a tsv file
     
  def ReadAll(self):
    # Reads the entire file
    # Output: json string
    self._OpenFile()
    lines = self._fh.readlines()
    self._CloseFile()
    lst = []
    n = 0  # line number
    for line in lines:
      n += 1
      if n == 1:
        continue  # Skip the header line
      dic = {}
      colvals = line.split()
      if len(colvals) != len(self._colnames):
        msg = "Inconsistent column format in file %s in line %n" % (
            self._filename, n)
        raise FileError(msg)
      for i in range(len(colvals)):
        dic[self._colnames[i]] = ut.ConvertType(colvals[i])
      lst.append(dic)
    result = json.dumps(lst)
    return result


class CrdFile2Json(_FileBase):
  # Creates ordinates and point values for a structured tsv file in which
  # each row in the file is a point consisting of successive columns for
  #  y coordinate
  #  x coordinate
  #  value at the x,y point
  # The first line is header that specifies the names of the columns
  # Coordinate values are ordered by their sequence of occurrence
  # Points are an array of dictionaries consisting of the x position,
  # y position, and value.
  NUM_COLS = 3

  def __init__(self, filename):
    self._xcrds = []
    self._ycrds = []
    self._points = []
    super(CrdFile2Json, self).__init__(filename)

  def _GetCoord(self, coord_type, coord_value):
    # Returns the offset index of the coordinate value
    # Input: coord_type - "x" or "y"
    #        coord_value - character value of the coordinate
    # Output: index of the coordinate
    # Exception: raise InternalError if coordinate doesn't exist
    if coord_type == "x":
      coords = self._xcrds
    else:
      if coord_type == "y":
        coords = self._ycrds
      else:
        raise InternalError("Invalid coord_type - %s" % coord_type)
    result = coords.index(coord_value) + 1
    if result is None:
      msg = "Invalid coordinate %s for coordinate type %s in file %s on line %n" % (
          coord_value, coord_type, self._filename, n)
      raise InternalError(msg)
    return result

  def ReadAll(self):
    # Processes the file. Results are retrived using GetXCrds, GetYCrds, GetPoints
    # Get the file data
    self._OpenFile()
    lines = self._fh.readlines()
    self._CloseFile()
    n = 0  # line number
    # Iterate across all rows in the file
    for line in lines:
      n += 1
      if n == 1:
        continue  # Skip the header line
      colvals = line.split()
      if len(colvals) != CrdFile2Json.NUM_COLS:
        msg = "Inconsistent column format in file %s in line %n" % (
            self._filename, n)
        raise FileError(msg)
      ycrd = colvals[0]
      xcrd = colvals[1]
      val = colvals[2]
      # Update the coordinates
      try:
        self._ycrds.index(ycrd)
      except:
        self._ycrds.append(ycrd)
      try:
        self._xcrds.index(xcrd)
      except:
        self._xcrds.append(xcrd)
      # Populate the dictionary for this point
      dic = {
          "y": self._GetCoord("y", ycrd),
          "x": self._GetCoord("x", xcrd),
          "value": ut.ConvertType(val),
          }
      self._points.append(dic)

  def GetXCrds(self):
    return json.dumps(self._xcrds)

  def GetYCrds(self):
    return json.dumps(self._ycrds)

  def GetPoints(self):
    return json.dumps(self._points)

  def GetHeaders(self):
    return self._colnames

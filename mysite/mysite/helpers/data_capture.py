"""
Capture data for use elsewhere
"""

from mysite import settings
import os
import pickle


class DataCapture(object):

  """
  Capture and recover data for use elsewhere.
  """

  def __init__(self, filename, directory=settings.SCISHEETS_TEST_DIR):
    """
    :param str filename: filename without extension
    :param str directory: directory path where file is placed
    """
    self._filename = filename
    self._directory = directory
    self._filepath = os.path.join(self._directory, 
        "%s.pcl" % self._filename)


  def setData(self, data):
    """
    Capture data and put it into a PCL file to use in testing.
    Data are placed into the test directory
    :param list-of-object data: data to be captured
    """
    pickle.dump(data, open(self._filepath, "wb"))

  def getData(self):
    """
    :returns list-of-object: same objects saved
    """
    fh = open(self._filepath, "rb")
    data = pickle.load(fh)
    fh.close()
    return data

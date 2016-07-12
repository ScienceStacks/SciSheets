"""Provides logging in a CSV format."""

import time


_HEADER = '"cumtime (ms)", "last_elapsed (ms)", "name", "details"'

class Logger(object):

  """Tracks culmulative and relative time."""

  def __init__(self, filepath, logger_name):
    self._filepath = filepath
    self._logger_name = logger_name
    self._write(_HEADER, is_initialize=True)
    self._last_time = time.time()
    self._cumtime = 0

  def _write(self, line, is_initialize=False):
    """
    :param str line: line to write
    :param bool is_initialize: write w/o append
    :raises IOError:
    """
    if is_initialize:
      mode = "w"
    else:
      mode = "a"
    with open(self._filepath, mode) as fh:
      fh.write("%s\n" % line)

  def log(self, name, details=""):
    """
    Writes a log entry
    """
    last_elapsed = 1000*(time.time() - self._last_time)
    self._cumtime += last_elapsed
    line = '%f, %f, "%s/%s", "%s"' % (
                               self._cumtime,
                               last_elapsed,
                               self._logger_name,
                               name,
                               details
                              )
    self._write(line)
    self._last_time = time.time()
    
    

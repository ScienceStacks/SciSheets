"""
Accumulates and outputs indented statements
"""

import sys
import os


######################## CLASSES ####################
class StatementAccumulator(object):
  """
  Accumulates statements in lists, providing
  appropriate indentation.
  The same statement may be written to multiple lists.
  """

  def __init__(self):
    self._statements = []
    self._indent_level = 0

  def indent(self, size, isIncremental=True):
    """
    Adjusts the indentation for statements.
    :param int size: amount of indent
    :param bool isIncremental: if True, incremental change;
                               else, absolute
    """
    if isIncremental:
      self._indent_level += size
    else:
      self._indent_level = size

  def add(self, new_statements):
    """
    :param str or list-of-str new_statements: python statements
    """
    if isinstance(new_statements, str)  \
        or isinstance(new_statements, unicode):
      new_statements = [new_statements]
    self._statements.extend(self._indent(new_statements))

  def get(self):
    """
    :return str: string for the statements accumulated
    :raises ValueError: if number of name is not specified
                        and more than one name is present
    """
    return '\n'.join(self._statements)

  def _indent(self, new_statements):
    """
    :param list-of-str new_statements:
    :return: list of indented statements
    """
    indents = " " * 2*self._indent_level
    result = [s.replace("\n", "\n" + indents)  \
        for s in new_statements]
    result = ["%s%s" % (indents, s) for s in result]
    return result

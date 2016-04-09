"""
Manages statements generated during compilation.
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

  def __init__(self, names):
    """
    :param list-of-str names: identifiers the lists
    """
    self._statement_lists = {}
    self._indent_level = 0
    for name in names:
      self._statement_lists[name] = []

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

  def add(self, statements, names=None):
    """
    :param str or list-of-str statements: python statements
    :param list-of-str names: lists to which statements should be appended.
                              if None, appended to all lists
    """
    if isinstance(statements, str):
      statements = [statements]
    if names is None:
      names = self._statement_lists.keys()
    for name in names:
      self._statement_lists[name].extend(self._indent(statements))

  def clear(self, name):
    """
    :param str name: name to remove
    """
    self._statement_lists[name] = []

  def get(self, name=None):
    """
    :param str name: name of statement list to return
    :return str: string for the statements accumulated
    :raises ValueError: if number of name is not specified
                        and more than one name is present
    """
    if name is None:
      names = self._statement_lists.keys()
      if len(names) > 1:
        raise ValueError("Must specify name if names >1.")
      name = names[0]
    return '\n'.join(self._statement_lists[name])

  def _indent(self, statements):
    """
    :param list-of-str statements:
    :return: list of indented statements
    """
    indents = " " * 2*self._indent_level
    result = [s.replace("\n", "\n" + indents) for s in statements]
    result = ["%s%s" % (indents, s) for s in result]
    return result

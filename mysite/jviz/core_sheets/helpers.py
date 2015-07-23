''' Helper classes for sheets. '''

import errors as er


class OrderableStrings(object):
  '''
  Provide an orderable collection of strings. Allows for inserting,
  removing, changing the order of strings.
  Name conventions:
    ref - either a string or an int
    refint - reference that's an integer
    refstg - reference that's a string
  '''

  def __init__(self):
    self._orderable_strings = {}  # keys are strings; values are positions

  def _ChangePositions(self, ref, increment):
    # Change positions p > position of a reference string to p+increment
    # Input: ref - ref to the string whose position is used as a reference
    #        increment - integer amount of change
    refstg = self._RefToStg(ref)
    for s in self._orderable_strings.keys():
      if self._orderable_strings[s] > self._orderable_strings[refstg]:
        self._orderable_strings[s] += increment

  def _RefToPos(self, ref):
    if isinstance(ref, int):
      return ref
    if isinstance(ref, stg):
      return self._orderable_strings[ref]
    raise er.InternalError("Invalid type to convert to a string: %g" % ref)

  def _RefToStg(self, ref):
    if isinstance(ref, int):
      return self.GetString(ref)
    if isinstance(ref, str):
      return ref
    raise er.InternalError("Invalid type to convert to a string: %g" % ref)

  def Append(self, stg, NoDuplicate=True):
    if NoDuplicate and stg in self._orderable_strings.keys():
      raise er.InternalError("Append: Ordered list already has string %s" % stg)
    pos = len(self._orderable_strings.values())
    self._orderable_strings[stg] = pos

  def Delete(self, stg):
    if not self._orderable_strings.has_key(stg):
      raise er.InternalError("Delete: Ordered list doesn't have string %s" % stg)
    self._ChangePositions(stg, -1)
    del self._orderable_strings[stg]

  def GetMaxPosition(self):
    return max(self._orderable_strings.values())
    
  def GetPosition(self, stg):
    # Returns the position for the specified string
    if stg in self._orderable_strings.keys():
      return self._orderable_strings[stg]
    raise er.InternalError("String %s not found.") % stg

  def GetStrings(self):
    return self._ordered_string.keys()

  def GetString(self, pos):
    # Returns the string at the specified position
    for s,p in self._orderable_strings.iteritems():
      if p == pos:
        return s
    raise er.InternalError("pos has no matching string" % pos)

  def Insert(self, stg, ref):
    # Inserts a string at the position currently occupied by ref
    # Input: stg - string to insert
    #        ref - either a string or a position
    refint = self._RefToPos(ref)
    move_pos = refint - 1  # Move the reference string as well
    self.ChangePositions(move_pos, 1)

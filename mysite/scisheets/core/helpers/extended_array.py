"""Extend numpy array with meta data."""

import numpy as np
import collections

def makeIterable(val):
  """
  Ensures that val is an iterable
  :param object val:
  :return collections.Iterable:
  """
  if isinstance(val, collections.Iterable):
    return val
  else:
    return [val]

class ExtendedArray(np.ndarray):

  """Adds a name property."""

  def __new__(
    cls,
    values                  = None,
    name                    = None,
    tree                    = None, # tree object
    eventNumber             = None,
    eventWeight             = None,
    numberOfBins            = None, # binning
    binningLogicSystem      = None, # binning
    ):
    if values is None:
      values = []
    values = makeIterable(values)
    self = np.asarray(values).view(cls)
    self.name               = name
    self.tree               = tree
    self.eventNumber        = eventNumber
    self.eventWeight        = eventWeight
    self.numberOfBins       = numberOfBins
    self.binningLogicSystem = binningLogicSystem
    return self

  def setName(self, name):
    self.name = name

  def __len__(self):
    try:
      length = len(self.tolist())
    except TypeError:
      length = 1
    return length

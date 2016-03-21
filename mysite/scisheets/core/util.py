'''Utilities used in core scitable code.'''

import collections
import math
import numpy as np

DTYPE_STRING = '|S1000'

################ Internal Classes ################
class XInt(object):
  """
  Extends int type by allowing strings of int.
  Note that in python 1 is equivalent to True
  and 0 is equivalent to False.
  """
  
  @classmethod
  def isBaseType(cls, val):
    """
    Checks if the value is an instance of the
    base type extended by this class.
    :param val: value to check if it's a base type
    :return: True if base type; otherwise False
    """
    return isinstance(val, int)
  
  @classmethod
  def isXType(cls, val):
    """
    Checks if the value is an instance of the extended type
    defined by this class.
    :param val: value to check if it's an extended type
    :return: True if extended type; otherwise False.
    """
    if cls.isBaseType (val):
      return True
    if isinstance(val, str):
      return isinstance(int(val), int)

  @classmethod
  def isCorecible(cls, val):
    """
    Checks if the value can be coerced to the base type for this class.
    :param val: value to check
    :return: True if coercible; otherwise, False.
    """
    return cls.isXType(val)

  @classmethod
  def coerce(cls, val):
    """
    Converts an a coercible value to the base type
    :param val: value to convert
    :return: coerced value
    """
    try:
      return int(val)
    except ValueError:
      raise ValueError("%s is not a %s" % (str(val), str(cls)))


class XFloat(object):
  """
  Extends float type by allowing strings of float
  and None. None is converted to np.nan
  """
  
  @classmethod
  def isBaseType(cls, val):
    """
    Checks if the value is an instance of the
    base type extended by this class.
    :param val: value to check if it's a base type
    :return: True if base type; otherwise False
    """
    return isinstance(val, float)
  
  @classmethod
  def isXType(cls, val):
    """
    Checks if the value is an instance of the extended type
    defined by this class.
    :param val: value to check if it's an extended type
    :return: True if extended type; otherwise False.
    """
    if cls.isBaseType (val):
      return True
    if isinstance(val, str):
      return isinstance(float(val), float)

  @classmethod
  def isCorecible(cls, val):
    """
    Checks if the value can be coerced to the base type for this class.
    :param val: value to check
    :return: True if coercible; otherwise, False.
    """
    return cls.isXType(val) or (val is None)

  @classmethod
  def coerce(cls, val):
    """
    Converts an a coercible value to the base type
    :param val: value to convert
    :return: coerced value
    :raises ValueError:
    """
    try:
      if val is None:
        return np.nan
      return float(val)
    except ValueError:
      raise ValueError("%s is not a %s" % (str(val), str(cls)))


class XBool(object):
  """
  Extends Boolean type by allowing the strings
  'True' and 'False'
  """
  
  @classmethod
  def isBaseType(cls, val):
    """
    Checks if the value is an instance of the base type.
    :param val: value to check
    :return: True if base type; otherwise False
    Note: python can treat 1.0 as True
    """
    return (not isinstance(val, float)) and val in [True, False]
  
  @classmethod
  def isXType(cls, val):
    """
    Checks if the value is an instance of the extended type
    defined by this class.
    :param val: value to check if it's an extended type
    :return: True if extended type; otherwise False.
    """
    return cls.isBaseType (val)  \
           or val in ['True', 'False']

  @classmethod
  def isCorecible(cls, val):
    """
    Checks if the value can be coerced
    :param val: value to check
    :return: boolean
    """
    return cls.isXType(val)

  @classmethod
  def coerce(cls, val):
    """
    Converts an XBool to a bool
    :param val: XBool value to convert
    :return: bool
    """
    if val in [True, 'True']:
      return True
    if val in [False, 'False']:
      return False
    else:
      raise ValueError("Input is not %s." % str(cls))

################ Functions ################
# ToDo: Need tests
def findDatatypeForValues(values):
  """
  Determines the dominate numpy type ignoring None
  :param values: an enumerable
  :return: numpy type
  """
  array = np.array(values)
  if all([isinstance(v, str) for v in array]):
    return '|S1000'  # Maximum string length is 1000
  else:
    return array.dtype

def isNumbers(values):
  """
  :param values: single or multiple values
  :return: True if number; otherwise, fasle.
  """
  if not isinstance(values, collections.Iterable):
    values = [values]
  result = False
  for val in values:
    if isinstance(val, float) or isinstance(val, int):
      result = True
    else:
      try:
        if result and (val is not None) and (not math.isnan(val)):
          return False  # Mixed types
      except TypeError:
        return False
  return result

def isFloats(values):
  """
  :param values: single or multiple values
  :return: True if float or np.nan; otherwise, fasle.
  """
  if not isinstance(values, collections.Iterable):
    values = [values]
  dtype = np.array(values).dtype
  return dtype == np.float64  # pylint: disable=E1101

def makeArray(values):
  """
  Constructs a numpy array from the values, if possible.
  Constructs the most restrictive type (e.g., converting
  strings to Bool,if possible).
  :param values: singleton or iterable of values to make into an array
  :return: a numpy array
  """
  if not isinstance(values, collections.Iterable):
    values = [values]
  array = np.array(values)
  # Test to see if this is a Boolean
  new_values = [True if v == 'True' else
                False if v == 'False' else -1 for v in array]
  if not any([x == -1 for x in new_values]):
    array = np.array(new_values, dtype=np.bool)
  elif array.dtype.type is np.string_:  # pylint: disable=E1101
    array = np.array(values, dtype=DTYPE_STRING)
  return array

def getType(val):
  """
  Finds the most restrictive type for the value.
  :param val: value to interrogate
  :return: type of int, XInt, float, XFloat, bool, XBool, str, object, None
  """
  TT = collections.namedtuple('TypeTest', 'typ tst')
  types = [
           TT(XBool, (lambda x: XBool.isXType(x))),
           TT(XInt, (lambda x: XInt.isXType(x))),
           TT(XFloat, (lambda x: XFloat.isXType(x))),
           TT(None, (lambda x: x is None)),
           TT(str, (lambda x: isinstance(x, str))), # last test
          ]
  for dtype in types:
    try:
      if dtype.tst(val):
        return dtype.typ
    except ValueError:
      pass
  return object

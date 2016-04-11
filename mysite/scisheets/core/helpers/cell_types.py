'''Utilities used in core scitable code.'''

import collections
import math
import numpy as np


################ Internal Classes ################
class XType(object):
  """
  Code common to all extended types
  """

  @classmethod
  def needsCoercion(cls, types):
    """
    Checks if the iterables must be coerced
    :param list values: values to check
    :return bool: Should invoke coercion if True
    """
    return all([cls.isCoercible(t) for t in types])


class XInt(XType):
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
    :return bool: True if extended type; otherwise False.
    """
    if cls.isBaseType(val):
      return True
    if isinstance(val, str):
      return isinstance(int(val), int)
    if isinstance(val, float):
      return int(val) == val
    return False

  @classmethod
  def isCoercible(cls, a_type):
    """
    Checks if the type can be coerced to the base type for this class.
    :param a_type: type considered
    :return: True if coercible; otherwise, False.
    """
    return a_type in [XInt, int, XBool, bool]

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


class XFloat(XType):
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
  def isCoercible(cls, a_type):
    """
    Checks if the value can be coerced to the base type for this class.
    :param a_type: determines if the type can be coerced
    :return: True if coercible; otherwise, False.
    """
    return a_type in [XFloat, float, int, XInt, None, bool, XBool]

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


class XBool(XType):
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
  def isCoercible(cls, a_type):
    """
    Checks if the value can be coerced to the base type for this class.
    :param a_type: determines if the type can be coerced
    :return: True if coercible; otherwise, False.
    """
    return a_type in [bool, XBool]

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
def isFloats(values):
  """
  :param values: single or multiple values
  :return: True if float or np.nan; otherwise, fasle.
  """
  if not isinstance(values, collections.Iterable):
    values = [values]
  dtype = np.array(values).dtype
  return dtype == np.float64  # pylint: disable=E1101

def getType(val):
  """
  Finds the most restrictive type for the value.
  :param val: value to interrogate
  :return: type of int, XInt, float, XFloat, bool, XBool, str, object, None
  """
  TT = collections.namedtuple('TypeTest', 'typ chk')
  types_and_checkers = [
           TT(XBool, (lambda x: XBool.isXType(x))),
           TT(XInt, (lambda x: XInt.isXType(x))),
           TT(XFloat, (lambda x: XFloat.isXType(x))),
           TT(None, (lambda x: x is None)),
           TT(str, (lambda x: isinstance(x, str))), # last test
          ]
  for t_c in types_and_checkers:
    try:
      if t_c.chk(val):
        return t_c.typ
    except ValueError:
      pass
  return object

def coerceData(data):
  """
  Coreces data in a list to the most restrictive type so that
  the resulting list is treated correctly when constructing
  a numpy array.
  :param data: iterable
  :return type, list: coerced data if coercion was required
  """
  types = [getType(d) for d in data]
  # Check for conversion in order from the most restrictive
  # type to the most permissive type
  for x_type in [XBool, XInt, XFloat]: 
    if x_type.needsCoercion(types):
      return [x_type.coerce(d) for d in data]
  return list(data)

def isStrArray(array):
  """
  :param np.array array:
  :return bool:
  """
  return str(array.dtype)[0:2] == '|S'

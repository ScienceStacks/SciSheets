'''Utilities used in core scitable code.'''

from extended_array import ExtendedArray
from common_util.prune_nulls import pruneNulls
import collections
import math
import numpy as np
import warnings

THRESHOLD = 0.000001  # Threshold for value comparisons

################### Classes ############################
# Used to define a DataClass
# cls is the data type that can be tested in isinstance
# cons is a function that constructs an instance of cls
#   taking as an argument a list
# Usage: data_class = DataClass(cls=ExtendedArray,
#                               cons=(lambda(x: ExtendedArray(x))))
# Note: Classes must have a public property name that is the
#       name of the column
DataClass = collections.namedtuple('DataClass', 'cls cons')

########### CONSTANTS ################
def makeArray(aList):
  return ExtendedArray(values=aList)
DATACLASS_ARRAY = DataClass(cls=ExtendedArray,
    cons=makeArray)


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
    if isStr(val):
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
    if isStr(val):
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
    if isinstance(val, collections.Iterable) and not isStr(val):
      return False
    is_base = cls.isBaseType (val)
    is_bool = val in ['True', 'False']
    return is_base or is_bool

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
def isEquivalentFloats(val1, val2):
  """
  Determines if two floats are close enough to be equal.
  :param float val1, val2:
  :return bool:
  """
  try:
    if np.isnan(val1) and np.isnan(val2):
      result = True
    elif np.isnan(val1) or np.isnan(val2):
      result = False
    else:
      denom = max(abs(val1), abs(val2))
      if denom == 0:
        result = True
      else:
        diff = 1.0*abs(val1 - val2)/denom
        result = diff < THRESHOLD
  except ValueError:
    result = False
  return result

def isFloat(value):
  """
  :param object value:
  :return: True if float or np.nan; otherwise, fasle.
  """
  expected_type = getType(value)
  return expected_type == XFloat

def isFloats(values):
  """
  :param values: single or multiple values
  :return: True if float or np.nan; otherwise, fasle.
  """
  values = makeIterable(values)
  computed_type = getIterableType(values)
  expected_type = XFloat  # Must do assignment to get correct format
  return computed_type == expected_type

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
           TT(str, (lambda x: isinstance(x, str))), 
           TT(unicode, (lambda x: isinstance(x, unicode))), # last test
          ]
  for t_c in types_and_checkers:
    try:
      if t_c.chk(val):
        return t_c.typ
    except ValueError:
      pass
  return object

def getIterableType(values):
  """
  Finds the most restrictive type for the set of values
  :param values: iterable
  :return: type of int, XInt, float, XFloat, bool, XBool, str, object, None
  """
  types_of_values = [getType(x) for x in values]
  selected_types = [object, unicode, str, XFloat, XInt, XBool, None]
  for typ in selected_types:
    this_type = typ
    if this_type in types_of_values:
      return typ
  

def coerceData(data):
  """
  Coreces data in a list to the most restrictive type so that
  the resulting list is treated correctly when constructing
  a numpy array.
  :param data: iterable
  :return type, list: coerced data if coercion was required
  """
  data = makeIterable(data)
  types = [getType(d) for d in data]
  # Check for conversion in order from the most restrictive
  # type to the most permissive type
  for x_type in [XBool, XInt, XFloat]: 
    if x_type.needsCoercion(types):
      return [x_type.coerce(d) for d in data]
  return list(data)

def isIterable(val):
  """
  Verfies that the value truly is iterable
  :return bool: True if iterable
  """
  if isStr(val):
    return False
  return isinstance(val, collections.Iterable)

def isStr(val):
  """
  :param object val:
  :return bool:
  """
  return isinstance(val, str) or isinstance(val, unicode)

def isStrs(vals):
  """
  :param iterable vals:
  :return bool:
  """
  a_list = makeIterable(vals)
  return all([isStr(x) for x in a_list])
  #return str(array.dtype)[0:2] == '|S'

def makeIterable(val):
  """
  Converts val to a list
  :param object val:
  :return collections.Iterable:
  """
  if isinstance(val, collections.Iterable):
    #return val
    return [x for x in val]
  else:
    return [val]

def isEquivalentData(val1, val2):
  """
  Determines if two objects are equivalent. Recursively
  inspects iterables. 
  :param object val1, val2:
  :return bool:
  """
  warnings.filterwarnings('error')
  try:
    if isStr(val1) and isStr(val2):
      return val1 == val2  # Catch where this becomes a warning
  except Warning:
    import pdb; pdb.set_trace()
    pass
  if isIterable(val1):
    try:
      pruned_val1 = pruneNulls(val1)
      pruned_val2 = pruneNulls(val2)
      if len(pruned_val1) == len(pruned_val2):
        length = len(pruned_val1)
        for idx in range(length):
          if not isEquivalentData(pruned_val1[idx], pruned_val2[idx]):
            return False
        return True
      else:
        return False
    except TypeError as err:
      return False
  elif isinstance(val2, collections.Iterable) and not isStr(val2):
      return False
  else:
    if isFloat(val1) and  isEquivalentFloats(val1, val2):
      return True
    try:
      if val1 == val2:
        return True
    except:
      pass
    values = coerceData([val1, val2])
    coerced_val1 = values[0]
    coerced_val2 = values[1]
    if isFloat(coerced_val1):
      return isEquivalentFloats(coerced_val1, coerced_val2)
    else:
      return coerced_val1 == coerced_val2

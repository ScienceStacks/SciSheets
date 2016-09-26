"""
This module provides for serialization and deserialization of SciSheets Tables.
Serialization is done as JSON objects.
Usage:
  json_object = serialize(object)
  object = deserialize(json_object)
For a SciSheet object to be supported, it must implement the following methods:
  getSerializationDict - returns a dictionary of property names and their values
  deserialize(dict) - returns an object of the class using the properties in dict
  
"""
from mysite.helpers.util import stringToClass
import collections
import json


CLASS_VARIABLE = 'SciSheets_Class'

class SciSheetsEncoder(json.JSONEncoder):
  """
  Extends the standard encoder to handle SciSheet objects
  """
  def default(self, o):
    """
    :param object o: object to be serialized
    """
    if not isinstance(o, type):  # Don't process type objects
      if 'getSerializationDict' in dir(o):
        serialization_dict = o.getSerializationDict(CLASS_VARIABLE)
        return serialization_dict
      # All iterables are serialized as lists
      if isinstance(o, collections.Iterable):
        return [x for x in o]
    elif '__dict__' in dir(o):
      return o.__dict__
    else:
      return None

def serialize(instance):
  """
  Wrapper for serializing SciSheets objects
  """
  return json.dumps(instance, cls=SciSheetsEncoder,
      sort_keys=True,
      indent=2, separators=(',', ': '))

class SciSheetsJSONDecoder(json.JSONDecoder):

  def decode(self, json_string):
    """
    json_string is string that you give to json.loads method
    Simple decoder either returns a full decoded object
    or a properties dictionary
    """
    default_obj = super(SciSheetsJSONDecoder,self).decode(json_string)
    if isinstance(default_obj, list):
      obj_list = default_obj
      is_list = True
    else:
      obj_list = [default_obj]
      is_list = False
    results = []
    for obj in obj_list:
      if isinstance(obj, dict):
        if CLASS_VARIABLE in obj.keys():
          cls = stringToClass(obj[CLASS_VARIABLE])
          results.append(cls.deserialize(obj))
        else:
          results.append(obj)
      else:
        results.append(obj)
    if not is_list:
      return results[0]
    else:
      return results
    


def deserialize(json_string):
  return SciSheetsJSONDecoder().decode(json_string)

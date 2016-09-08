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
from scisheets.core.column import Column
from scisheets.core.table import Table
import json


CLASS_VARIABLE = 'SciSheets_Class'

class SciSheetssEncoder(json.JSONEncoder):
  """
  Extends the standard encoder to handle SciSheet objects
  """
  def default(self, o):
    """
    :param object o: object to be serialized
    """
    if ((not isinstance(o, type))  
       and 'getSerializationDict' in dir(o)):
      encode_dict = {CLASS_VARIABLE: str(o.__class__)}
      new_dict = o.getSerializationDict()
      encode_dict.update(new_dict)
      return encode_dict
    elif '__dict__' in dir(o):
      return o.__dict__
    else:
      return None

def serialize(instance):
  """
  Wrapper for serializing SciSheets objects
  """
  return SciSheetssEncoder().encode(instance)


class SciSheetsJSONDecoder(json.JSONDecoder):

  def stringToClass(self, obj_dict):
    """
    DYNAMICALLY CONSTRUCT THE CLASS SINCE HAVE THE FULL PATH
    u'SciSheets_Class': u"<class 'scisheets.core.helpers.test_serialize_deserialize.TestObject'>"
    """
    class_string = obj_dict[CLASS_VARIABLE]
    if 'Column' in class_string:
      return Column
    if 'Table' in class_string:
      return Table
    if 'TestObject' in class_string:
      import pdb; pdb.set_trace()
    raise ValueError('Unknown class %s' % class_string)

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
          import pdb; pdb.set_trace()
          cls = self.stringToClass(obj)
          del default_obj.__dict__[CLASS_VARIABLE]
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

'''Tests for serialization and deserialization'''

import serialize_deserialize as sd
import json
import unittest


#########################
class TestObject(object):

  def __init__(self, size):
    self.testing = 'Hello'
    self.a_list = range(size)

  def getSerializationDict(self):
    return {'testing': self.testing, 
        'range_length': len(self.a_list)}

  @classmethod
  def deserialize(cls, obj_dict):
    return TestObject(obj_dict['range_length'])
    

#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestFunctions(unittest.TestCase):

  def testSerializeBasic(self):
    return
    obj = {"a": range(10)}
    json_str = sd.serialize(obj)
    self.assertEqual(json.loads(json_str), obj)

  def testSerializeWithHook(self):
    return
    obj1 = range(10)
    obj2 = TestObject(5)
    json_str = sd.serialize([obj1, obj2])
    [new_obj1, obj2_dict] = json.loads(json_str)
    new_obj2 = TestObject(obj2_dict['range_length'])
    self.assertEqual(obj2.a_list, new_obj2.a_list)

  def testDeserializeBasic(self):
    return
    obj = range(10)
    json_str = sd.serialize(obj)
    new_obj = sd.deserialize(json_str)
    self.assertEqual(obj, new_obj)

  def testDeserializeWithHook(self):
    obj1 = range(10)
    obj2 = TestObject(5)
    json_str = sd.serialize([obj1, obj2])
    [new_obj1, new_obj2] = sd.deserialize(json_str)
    self.assertEqual(obj2.a_list, new_obj2.a_list)
    json_str = sd.serialize(obj2)
    new_obj2 = sd.deserialize(json_str)
    self.assertEqual(obj2.a_list, new_obj2.a_list)
 

if  __name__ == '__main__':
  unittest.main()

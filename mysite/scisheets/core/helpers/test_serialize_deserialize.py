'''Tests for serialization and deserialization'''

from scisheets.core.helpers_test import createColumn,  \
    setupTableInitialization
import scisheets.core.helpers.serialize_deserialize as sd
import numpy as np
import json
import unittest

# Constants
COLUMN_NAME = "DUMMY"
LIST = [2.1, 3.0]
VALID_FORMULA = "a + b*math.cos(x)"


#########################
class TestObject(object):

  def __init__(self, size):
    self.testing = 'Hello'
    self.a_list = range(size)

  def getSerializationDict(self, class_str):
    return {
        class_str: str(self.__class__),
        'testing': self.testing, 
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

  def testDeserializeWithHookForLists(self):
    obj = [np.array(range(x)) for x in range(5)]
    json_str = sd.serialize(obj)
    new_obj = sd.deserialize(json_str)
    self.assertEqual(len(obj), len(new_obj))
    pairs = zip(obj, new_obj)
    for o1, o2 in pairs:
      self.assertEqual(o1.tolist(), o2)

  def testForColumn(self):
    self.column = createColumn(COLUMN_NAME, data=LIST, table=None,
        formula=VALID_FORMULA)
    json_str = sd.serialize(self.column)
    new_column = sd.deserialize(json_str)
    self.assertTrue(self.column.isEquivalent(new_column))

  def testForTable(self):
    setupTableInitialization(self)
    json_str = sd.serialize(self.table)
    new_table = sd.deserialize(json_str)
    self.assertTrue(self.table.isEquivalent(new_table))

 

if  __name__ == '__main__':
  unittest.main()

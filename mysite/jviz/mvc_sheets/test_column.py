'''Tests for column'''

from django.test import TestCase 
from jviz.mvc_sheets import column as cl
import numpy as np

# Constants
COLUMN_NAME = "DUMMY"
LIST = [2.0, 3.0]
TABLE = 'DUMMY'
FORMULA = "A+B"

#############################
# Utility Functions
#############################
def ToList(v):
  if isinstance(v, list):
    data_list = v
  elif isinstance(v, np.ndarray):
    data_list = v.tolist()
  else:
    data_list = [v]
  return data_list

def CompareValues(v1, v2):
  list1 = ToList(v1)
  list2 = ToList(v2)
  if len(list1) != len(list2):
    return False
  r = True
  for n in range(len(list1)):
    r = r and (list1[n] == list2[n])
  return r

def CreateColumn(name, data=np.array([]), table=None, formula=None):
  # Returns a populated column
  column = cl.Column(name)
  column.AddCells(data)
  column.SetTable(table)
  column.SetFormula(formula)
  return column


#############################
# Tests
#############################
class TestHelpers(TestCase):

  def testConstructor(self):
    column = cl.Column(COLUMN_NAME)
    self.assertEqual(column._name, COLUMN_NAME)
    self.assertIsNone(column._table)
    self.assertIsNone(column._formula)

  def testAddCells(self):
    SINGLE = 1.0
    LIST = [2.0, 3.0]
    ARRAY = np.array(LIST)
    column = cl.Column(COLUMN_NAME)
    column.AddCells(SINGLE)
    self.assertTrue(CompareValues(column._data_values, SINGLE))
    column = cl.Column(COLUMN_NAME)
    column.AddCells(LIST)
    self.assertTrue(CompareValues(column._data_values, LIST))
    column = cl.Column(COLUMN_NAME)
    column.AddCells(ARRAY)
    self.assertTrue(CompareValues(column._data_values, ARRAY))

  def testCopy(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    column_copy = column.Copy()
    self.assertEqual(column._name, column_copy._name)
    self.assertTrue(CompareValues(column._data_values, column_copy._data_values))
    self.assertEqual(column._formula, column_copy._formula)
    self.assertIsNone(column_copy._table)

  def testDelCells(self):
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    column.DelCells()
    self.assertEqual(len(column._data_values), 0)
    column = CreateColumn(COLUMN_NAME, data=LIST, table=TABLE,
        formula=FORMULA)
    INDEX = 0
    NON_INDEX = 1
    column.DelCells([INDEX])
    self.assertEqual(column._data_values[INDEX], LIST[NON_INDEX])
    


if __name__ == '__main__':
    unittest.main()

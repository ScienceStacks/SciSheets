'''Tests for formulas API'''

from api import API, APIFormulas, APIPlugin, APIAdmin
import helpers_test as ht
from helpers.trinary import Trinary
import table_evaluator as te
import numpy as np
import os
import pandas as pd
import unittest

COLUMN1 = "Col_1"
COLUMN2 = "Col_2"
COLUMN3 = "Col_3"
TRUTH_COLUMNS = ['A', 'B']
COLUMN1_VALUES = range(10)

#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestAPI(unittest.TestCase):

  def setUp(self):
    self.api = API()
    self.api._table = ht.createTable("test", column_name=COLUMN1)
    self.column1 = self.api._table.columnFromName(COLUMN1)
    self.column1.addCells(COLUMN1_VALUES, replace=True)
    ht.setupTableInitialization(self)

  def testGetColumnValues(self):
    values = self.api.getColumnValues(COLUMN1)
    self.assertTrue(all(values == COLUMN1_VALUES))

  def testSetColumnValues(self):
    new_column1_values = list(COLUMN1_VALUES)
    new_column1_values.extend(range(5))
    self.api.setColumnValues(COLUMN1, new_column1_values)
    values = self.api.getColumnValues(COLUMN1)
    self.assertTrue(all(values == np.array(new_column1_values)))

  def testColumnVisibility(self):
    names = ['row']
    column = self.api._table.columnFromName(names[0])
    self.assertEqual(len(self.api._table._hidden_columns), 0)
    self.api.setColumnVisibility(names, is_visible=False)
    self.assertEqual(len(self.api._table._hidden_columns), 1)
    self.assertTrue(column in self.api._table._hidden_columns)
    self.api.setColumnVisibility(names, is_visible=True)
    self.assertEqual(len(self.api._table._hidden_columns), 0)
    

# pylint: disable=W0212,C0111,R0904
class TestAPIFormulas(unittest.TestCase):

  def setUp(self):
    table = ht.createTable("test", column_name=COLUMN1)
    self.api = APIFormulas(table)
    ht.setupTableInitialization(self)

  def testGetValidatedColumn(self):
    column = self.api.getColumn(COLUMN1)
    self.assertEqual(column.getName(), COLUMN1)

  def _createColumn(self):
    self.api.createColumn(COLUMN2)
    return self.api.getColumn(COLUMN2)

  def testCreateColumn(self):
    column = self._createColumn()
    self.assertEqual(column.getName(), COLUMN2)

  def testDeleteColumn(self):
    _ = self._createColumn()
    self.api.deleteColumn(COLUMN2)
    is_absent = all([c.getName() != COLUMN2  \
        for c in self.api._table.getColumns()])
    self.assertTrue(is_absent)
    _ = self._createColumn()
    self.api.deleteColumn(2)
    is_absent = all([c.getName() != COLUMN2  \
        for c in self.api._table.getColumns()])
    self.assertTrue(is_absent)

  def testCreateTruthTable(self):
    return
    self._createTruthTable()
    for n in range(len(TRUTH_COLUMNS)):
      self.assertTrue(any([c.getName() == TRUTH_COLUMNS[n]
          for c in self.api._table.getColumns()]))

  def _createDataframe(self, prefix="", names=None):
    df = pd.DataFrame()
    data = {}
    if names is None:
      names = ["%sDUMMY%d_COLUMN" % (prefix, n) for n in [1,2,5]]
    if len(names) >= 3:
      data[names[2]] = [100.0, 200.0, 300.0]
    if len(names) >= 2:
      data[names[1]] = [10.1, 20.0, 30.0]
    if len(names) >= 1:
      data[names[0]] = ["one", "two", "three"]
    for name in names:
      df[name] = data[name]
    return df

  def _TableEqualDataframe(self, table, dataframe, names=None):
    if names is None:
      names = list(set(dataframe.columns).union(  \
           table.getColumnNames()))
    num = len(names)
    for name in dataframe.columns:
      column = table.columnFromName(name)
      b = all([dataframe[name][n] == column.getCells()[n]  \
               for n in range(num)])
      self.assertTrue(b)

  def testCreateFromDataframe(self):
    df = self._createDataframe()
    table = self.api.dataframeToTable("NewTable", df)
    num = len(df.columns)
    for name in df.columns:
      column = table.columnFromName(name)
      b = all([df[name][n] == column.getCells()[n]  \
               for n in range(num)])
      self.assertTrue(b)

  def _testAddFromDataframe(self, prefix="", names=None):
    df = self._createDataframe(prefix=prefix)
    self.api.addColumnsToTableFromDataframe(df, names=names)
    num = len(df.columns)
    if names is None:
      names = list(df.columns)
    self._TableEqualDataframe(self.api._table, df, names=names)

  def testAddFromDataframe(self):
    self._testAddFromDataframe()  # Name conflicts
    self._testAddFromDataframe(names=['DUMMY1_COLUMN'])
    self._testAddFromDataframe(prefix="D")  # No name conflicts
    self._testAddFromDataframe(prefix="D", 
        names=['DDUMMY1_COLUMN', 'DDUMMY2_COLUMN'])

  def _testToDataframe(self, names=None):
    df = self.api.tableToDataframe(columns=names)
    expected_df = self._createDataframe(names=names)
    self.assertEqual(len(df.columns), len(expected_df.columns))
    for name in df.columns:
      self.assertTrue(list(df[name]) == list(expected_df[name]))

  def testToDataframe(self):
    self.api._table = self.table
    self._testToDataframe()
    self._testToDataframe(names=['DUMMY1_COLUMN'])
    

# pylint: disable=W0212,C0111,R0904
class TestAPIPlugin(unittest.TestCase):

  def setUp(self):
    table = ht.createTable("test", column_name=COLUMN1)
    self.api = APIPlugin(table.getFilepath())
    self.api.initialize()
    ht.setupTableInitialization(self)

  def testDependencyCounter(self):
    self.assertEqual(self.api.getDependencyCounter(), 0)
    self.api.createColumn(COLUMN2)
    self.assertEqual(self.api.getDependencyCounter(), 1)
    self.api.deleteColumn(COLUMN2)
    self.assertEqual(self.api.getDependencyCounter(), 2)
    self.api.setDependencyCounter()
    self.assertEqual(self.api.getDependencyCounter(), 0)


# pylint: disable=W0212,C0111,R0904
class TestAPIAdmin(unittest.TestCase):

  def setUp(self):
    table = ht.createTable("test", column_name=[COLUMN1, COLUMN2])
    self.api = APIAdmin(table.getFilepath())
    self.api.initialize()
    ht.setupTableInitialization(self)


if __name__ == '__main__':
  unittest.main()

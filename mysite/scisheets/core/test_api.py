'''Tests for formulas API'''

from api import API, APIFormulas, APIPlugin, APIAdmin
from column import Column
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
TEST_FILE1 = "test_api_1"

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
    values = self.api.getColumnValue(COLUMN1)
    self.assertTrue(all(values == COLUMN1_VALUES))

  def testSetColumnValues(self):
    new_column1_values = list(COLUMN1_VALUES)
    new_column1_values.extend(range(5))
    self.api.setColumnValue(COLUMN1, new_column1_values)
    values = self.api.getColumnValue(COLUMN1)
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

  def testSetColumnVariables(self):
    table = self.api.getTable()
    self.api.setColumnVariables()
    for column in table.getColumns():
      self.assertTrue(column.getName() in table.getNamespace())
    new_column_name = "New_Column"
    new_column = Column(new_column_name)
    table.addColumn(new_column)
    self.api.setColumnVariables()
    self.assertTrue(new_column_name in table.getNamespace())

  def testSetColumnVariablesWithColnmsOption(self):
    table = self.api.getTable()
    self.api.setColumnVariables()
    old_cv_dict = {cv.getName(): cv 
        for cv in self.api.getColumnVariables()}
    self.api.setColumnVariables(colnms=[COLUMN1])
    cv_names = [cv.getName() for cv in self.api.getColumnVariables()]
    self.assertTrue(COLUMN1 in cv_names)
    for cv_name in cv_names:
      if cv_name != COLUMN1:
        self.assertEqual(old_cv_dict[cv_name], 
            self.api.getColumnVariable(cv_name))
    

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
    return  # Don't test TruthTable since not completed
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

  def testAddColumnsToDataframeMissingTable(self):
    table = self.api.getTable()
    df, names = table.getCapture(TEST_FILE1)
    column_names = [c.getName() for c in table.getColumns()]
    for name in names:
      self.assertFalse(name in column_names)
    self.api.addColumnsToTableFromDataframe(df, names=names)
    column_names = [c.getName() for c in table.getColumns()]
    for name in names:
      self.assertTrue(name in column_names)
      column = table.columnFromName(name)
      self.assertIsNotNone(column.getTable())

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

# pylint: disable=W0212,C0111,R0904
class TestAPIAdmin(unittest.TestCase):

  def setUp(self):
    table = ht.createTable("test", column_name=[COLUMN1, COLUMN2])
    self.api = APIAdmin(table.getFilepath())
    self.api.initialize()
    ht.setupTableInitialization(self)


if __name__ == '__main__':
  unittest.main()

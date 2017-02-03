'''Tests for UITable for Table Commands.'''

from mysite import settings
from scisheets.core.helpers.serialize_deserialize import serialize,  \
    deserialize
from scisheets.core.column import Column
from scisheets.core.table import NAME_COLUMN_STR
import ui_table as ui
from django.test import TestCase  # Provides mocks
import json


# Constants
COLUMN_NAMES = ['A', 'B', 'C']
DATA = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
DATA_STRING = ['AA', 'BB', 'CC']
NCOL = 30
NROW = 3
TABLE_NAME = "MY_TABLE"
IGNORE_TEST = True
    

class TestUITableCell(TestCase):

  def setUp(self):
    self.table = ui.UITable.createRandomHierarchicalTable(TABLE_NAME, 
        NROW, 3*NCOL, 0.3, prob_detach=0.2)

  def testProcessCommandTableDelete(self):
    if IGNORE_TEST:
      return

  def createNestedTable(self):
    """
    Table
      A
      B
      Subtable
        C
        D
    :return dict: name, object pairs
    """
    if IGNORE_TEST:
      return
    table = ui.UITable("Table")
    result = {"Table": table}
    result["A"] = Column("A")
    table.addColumn(result["A"])
    result["B"] = Column("B")
    table.addColumn(result["B"])
    subtable = ui.UITable("Subtable")
    result["Subtable"] = subtable
    table.addChild(subtable)
    result["C"] = Column("C")
    subtable.addColumn(result["C"])
    result["D"] = Column("D")
    subtable.addColumn(result["D"])
    return result
    

if __name__ == '__main__':
    unittest.man()

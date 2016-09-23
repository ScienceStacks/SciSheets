'''Tests for Trinary codes.'''

# TODO: TEST THIS!

#from plugin_trinary import createTrinary, createTruthTable
import unittest


class TestTrinary(unittest.TestCase):

  def _createTruthTable(self):
    return
    self.api.deleteColumn(COLUMN1)
    self.api.createTruthTable(TRUTH_COLUMNS, only_boolean = True)

  def testCreateTrinary(self):
    return
    self._createTruthTable()
    for n in range(len(TRUTH_COLUMNS)):
      column = self.api._table.columnFromName(TRUTH_COLUMNS[n])
      trinary = createTrinary(column.getCells())
      new_trinary = -trinary
      self.assertTrue(isinstance(new_trinary, Trinary))

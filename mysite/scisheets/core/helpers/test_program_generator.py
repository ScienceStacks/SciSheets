'''Tests for program_generator'''

import program_generator as pg
import mysite.settings as settings
from scisheets.core.helpers_test import createTable,  \
    stdoutIO, TableFileHelper, TEST_DIR
from scisheets.core import column as cl
from api_util import writeObjectToFile
import os
import numpy as np
import shutil
import unittest


# Constants
COLUMN = "DUMMY"
COLUMN1 = "DUMMY1"
COLUMN2 = "A"
COLUMN3 = "DUMMY3"
COLUMN4 = "DUMMY4"
COLUMN5 = "B"
COLUMNC = "C"
COLUMN_VALID_FORMULA = "VALID_FORMULA"
COLUMN_INVALID_FORMULA = "INVALID_FORMULA"
TABLE_NAME = "DUMMY_TABLE"
LIST = [2.0, 3.0]
LIST2 = [3.0]
TABLE = 'DUMMY'
VALID_FORMULA = "np.sin(A) + B"
VALID_FORMULA_WITH_USER_FUNCTION = "np.sin(A) + timesTwo(B)"
SECOND_VALID_FORMULA = "np.cos(C)"
INVALID_FORMULA = "np.cun(A)" # Invalid function
COLUMN1_CELLS = ["one", "two", "three"]
COLUMN2_CELLS = [10.0, 20.0, 30.0]
COLUMN5_CELLS = [100.0, 200.0, 300.0]
COLUMNC_CELLS = [1000.0, 2000.0, 3000.0]
IMPORT_PATHS = ["", "scisheets.core"]


#############################
# Helper Functions
#############################
def _compile(statements):
  """
  Compiles the statements
  :param str statements:
  :return str/None: None if no error
  """
  error = None
  try:
    compile(statements, "string", "exec")
  except SyntaxError as err:
    error = str(err)
  return error


#############################
# Tests
#############################
# pylint: disable=W0212
# pylint: disable=C0111
# pylint: disable=R0904
class TestFunctions(unittest.TestCase):
 
  def testMakeOutputStr(self):
    result = pg._makeOutputStr(["a"])
    self.assertEqual(result, "a")
    result = pg._makeOutputStr(["a", "b"])
    self.assertEqual(result, "a,b")
    result = pg._makeOutputStr([])
    self.assertEqual(result, "")

  def testMakeFunctionStatement(self):
    statement = pg._makeFunctionStatement("func", ["a", "bb"])
    expected = "def func(a, bb):"
    self.assertEqual(statement, expected)
    statement = pg._makeFunctionStatement("func", [])
    expected = "def func():"
    self.assertEqual(statement, expected)
    statement = pg._makeFunctionStatement("func", ["a"])
    expected = "def func(a):"
    self.assertEqual(statement, expected)


class TestProgramGenerator(unittest.TestCase):

  def setUp(self):
    self.table = createTable(TABLE_NAME)
    self._addColumn(COLUMN1, cells=COLUMN1_CELLS)
    self.column_a = self._addColumn(COLUMN2, cells=COLUMN2_CELLS)
    self.column_b = self._addColumn(COLUMN5, cells=COLUMN5_CELLS)
    self.column_c = self._addColumn(COLUMNC, cells=COLUMNC_CELLS)
    self.column_valid_formula = self._addColumn(COLUMN_VALID_FORMULA,
                                                formula=VALID_FORMULA)
    writeObjectToFile(self.table)
    self.generator = pg.ProgramGenerator(self.table, TEST_DIR)

  def _addColumn(self, name, cells=None, formula=None):
    column = cl.Column(name)
    if formula is not None:
      column.setFormula(formula)
    if cells is not None:
      column.addCells(cells)
    self.table.addColumn(column)
    return column

  def testFindFileNames(self):
    filename = "dummy"
    helper = TableFileHelper(filename, TEST_DIR)
    helper.create()
    python_files = self.generator._findFilenames(  \
        self.generator._user_directory)
    self.assertTrue(python_files.index(filename) > -1)
    helper.destroy()

  def testMakeFormulaImportStatementsForPlugin(self):
    statements = self.generator._makeFormulaImportStatements(  \
        self.generator._plugin_directory,
        import_path=self.generator._plugin_path)
    self.assertEqual(len(statements), 0)
    self.column_valid_formula.setFormula("intercept()")
    statements = self.generator._makeFormulaImportStatements(  \
        self.generator._plugin_directory,
        import_path=self.generator._plugin_path)
    expected = "from scisheets.plugins.intercept import intercept"
    self.assertEqual(statements, expected)

  def testMakeFormulaImportStatements(self):
    statements = self.generator._makeFormulaImportStatements(  \
        self.generator._user_directory)
    self.assertEqual(len(statements), 0)
    self.column_valid_formula.setFormula("dummy()")
    statements = self.generator._makeFormulaImportStatements(  \
        self.generator._user_directory)
    expected = "from dummy import dummy"
    self.assertEqual(statements, expected)

  def _testAssignmentStatements(self, function):
    """
    Function that returns assignment statements
    :param function function:
    """
    stg = "ColumnValue("
    statements = function()
    expected = self.table.numColumns()
    if expected != statements.count(stg):
      import pdb; pdb.set_trace()
    self.assertEqual(expected, statements.count(stg))
    statements = function(excludes=['row'])
    expected = self.table.numColumns() - 1
    self.assertEqual(expected, statements.count(stg))
    statements = function(only_includes=['row'])
    self.assertEqual(1, statements.count(stg))
    self.assertEqual(statements.count('row'), 2)
    self.assertIsNone(_compile(statements))

  def testAssignmentStatements(self):
    self._testAssignmentStatements(
        self.generator._makeColumnValuesAssignmentStatements)
    self._testAssignmentStatements(
        self.generator. _makeVariableAssignmentStatements)

  def testFormulaColumns(self):
    columns = self.generator._getFormulaColumns()
    self.assertEqual(columns[0].getName(), 'VALID_FORMULA')
    columns[0].removeTree()
    columns = self.generator._getFormulaColumns()
    self.assertEqual(len(columns), 0)

  def testMakeVariablePrintStatements(self):
    statements = self.generator._makeVariablePrintStatements()
    for column in self.table.getColumns():
      self.assertTrue(column.getName() in statements)

  def testMakePrologueAndEpilogueWithFormulas(self):
    statements = self.generator._makePrologue()
    self.assertTrue('import' in statements)
    self.assertIsNone(_compile(statements))
    statements = self.generator._makeEpilogue()
    self.assertTrue('s.controller.startBlock' in statements)
    self.assertIsNone(_compile(statements))

  def testMakePrologueWithoutFormulas(self):
    # Table without formulas
    self.table = createTable(TABLE_NAME)
    self._addColumn(COLUMN1, cells=COLUMN1_CELLS)
    self.column_a = self._addColumn(COLUMN2, cells=COLUMN2_CELLS)
    self.column_b = self._addColumn(COLUMN5, cells=COLUMN5_CELLS)
    self.column_c = self._addColumn(COLUMNC, cells=COLUMNC_CELLS)
    writeObjectToFile(self.table)
    self.generator = pg.ProgramGenerator(self.table, TEST_DIR)
    # Test Prologue and Epilogue
    statements = self.generator._makePrologue()
    self.assertTrue('import' in statements)
    self.assertIsNone(_compile(statements))
    statements = self.generator._makeEpilogue()
    self.assertTrue('s.controller.startBlock' in statements)
    self.assertIsNone(_compile(statements))

  def testMakeAPIPluginInitializationStatements(self):
    function_name = "this_test"
    statements = self.generator._makeAPIPluginInitializationStatements(
        function_name)
    statement_stg = "%s.%s" % (function_name, settings.SCISHEETS_EXT)
    self.assertTrue(statement_stg in statements)
    self.assertTrue("initialize()" in statements)
    self.assertIsNone(_compile(statements))

  def _checkWorkflow(self, program, tags):
    """
    Verifies that the tags occur in order in the program
    :param str program:
    :param list-of-str tags:
    """
    last_index = 0
    error = None
    for tag in tags:
      try:
        current_index = program.index(tag)
      except ValueError as err:
        import pdb; pdb.set_trace()
        error = str(err)
      self.assertIsNone(error)
      if not(last_index < current_index):
        import pdb; pdb.set_trace()
      self.assertTrue(last_index < current_index)
      last_index = current_index
    error = _compile(program)
    if error is not None:
      import pdb; pdb.set_trace()
    self.assertIsNone(_compile(program))

  def testMakeEvaluationScriptProgram(self):
    tags = ["import", "#_table", 
            "Prologue", "initializeLoop", 
            "isTerminateLoop", "startAnIteration", "np.sin",
            "endAnIteration"]
    program = self.generator.makeEvaluationScriptProgram()
    self._checkWorkflow(program, tags)
    tags = ["import", "_table", 
            "Prologue", "initializeLoop", 
            "isTerminateLoop", "startAnIteration", "np.sin",
            "endAnIteration"]
    program = self.generator.makeEvaluationScriptProgram(
        create_API_object=True)
    self._checkWorkflow(program, tags)

  def testMakeExportScriptProgram(self):
    tags = ["import", "_table", 
            "Prologue", "initializeLoop", 
            "isTerminateLoop", "startAnIteration", "np.sin",
            "endAnIteration", "print"]
    program = self.generator.makeExportScriptProgram()
    self._checkWorkflow(program, tags)

  def testMakeFunctionProgram(self):
    function_name = "my_func"
    inputs = ["A", "B"]
    outputs = ["C"]
    def_stmt = "def %s(" % function_name
    tags = [def_stmt, "import", "api.APIPlugin", \
        "numpy", "np.sin", "return"]
    program = self.generator.makeFunctionProgram(function_name,
                                               inputs,
                                               outputs)
    self._checkWorkflow(program, tags)

  def testMakeTestProgram(self):
    function_name = "my_func"
    inputs = ["A", "B"]
    output = "C"
    function_call = "%s = %s(" % (output, function_name)
    tags = ["import", "class ", "api.APIPlugin",  function_call,  \
        "self.assert"]
    program = self.generator.makeTestProgram(function_name,
                                           inputs,
                                           [output])
    self._checkWorkflow(program, tags)
    

if  __name__ == '__main__':
  unittest.main()

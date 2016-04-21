"""
Classes for controlling table evaluation and export.
"""

import helpers.api_util as api_util
from helpers.program_generator import API_OBJECT, ProgramGenerator
from helpers.program_runner import ProgramRunner
import sys
import os
import numpy as np

DEFAULT_USER_DIRECTORY = os.path.dirname(__file__)
GENERATED_FILE = "_GENERATED_FILE"


######################## CLASSES ####################
class TableEvaluator(object):
  """
  Coordinates the workflow for table evaluation and export:
    Compiling Python statements to evaluates formulas in a Table.
    Setting up the runtime environment.
      1. Write updated table to appropriate destination
      2. Create the API object for the script
    Running the compiled statements.
  The two main methods are:
    evaluate: evaluate formulas in a Table
    export: export a table as a function
  """

  def __init__(self, table):
    # Inputs: table - table to evaluate
    self._table = table

  def evaluate(self, user_directory=DEFAULT_USER_DIRECTORY):
    """
    Evaluates the formulas in a Table and assigns the results
    :param user_directory: path to user exported codes
    :param table_filepath: path to table file
    :return: errors from execution or None
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterate N (#formulas) times to handle dependencies
               between formulas
    """
    # Create the script program
    generator = ProgramGenerator(self._table, user_directory)
    program = generator.makeEvaluationScriptProgram()
    # Run the statements from a file
    runner = ProgramRunner(program, 
                       table=self._table,
                       user_directory=user_directory,  
                       pgm_filename=GENERATED_FILE)
    runner.writeFiles()
    return runner.execute(create_API_object=True)

  def export(self,
             function_name=None,
             inputs=None,
             outputs=None,
             user_directory=None):
    """
    Exports the table as python code
    :param function_name: string name of the function to be created
    :param inputs: list of column names that are input to the function
    :param outputs: list of columns that are output from the function
    :param user_directory: directory where user functions are located
    :return: error - string from the file export
    :sideeffects: (a) creates function file (<function_name>.py) in user_directory, 
                  (b) creates test file (test_<function_name>.py) in user_directory
    Notes: (1) Cannot put "exec" in another method
               since the objects created won't be accessible
           (2) Iterates N (#formulas) times to handle dependencies
               between formulas
    """
    # Initializations
    if inputs is None:
      inputs = []
    if outputs is None:
      outputs = []
    if function_name is None:
      function_name = DEFAULT_FUNCTION_NAME
    # Construct the function program
    generator = ProgramGenerator(self._table, user_directory)
    function_program = generator.makeFunctionProgram(function_name, 
                                                     inputs, 
                                                     outputs)
    # Write the function file
    runner = ProgramRunner(function_program, 
                           table=self._table,
                           user_directory=user_directory, 
                           pgm_filename=function_name)
    error = runner.writeFiles()
    if error is not None:
      return "Error constructing %s: %s" % (function_filepath, error)
    # Create the test file
    test_filename = "test_%s" % function_name
    test_program = generator.makeTestProgram(function_name, inputs, outputs)
    test_runner = ProgramRunner(test_program, 
                                table=self._table,
                                user_directory=user_directory, 
                                pgm_filename=test_filename)
    error = test_runner.writeFiles(write_table=False)
    if error is not None:
      return "Error constructing %s: %s" % (test_filepath, error)
    return None

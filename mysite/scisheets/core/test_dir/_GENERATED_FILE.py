# Evaluation of the table TEST.

    
from scisheets.core import api as api
# Uncomment the following to execute standalone
#
#_table = api.readTableFromFile('/Users/Fluids/Documents/SciSheets/mysite/scisheets/core/test_dir/TEST_TABLE.scish')
#_table.setNamespace(globals())
#s = api.APIFormulas(_table) 
#
try:
  
  s.controller.startBlock('Prologue')
  # Prologue
  import math as mt
  import numpy as np
  from os import listdir
  from os.path import isfile, join
  import pandas as pd
  import scipy as sp
  from numpy import nan  # Must follow sympy import 
  
  s.controller.endBlock()
  
  # Formula evaluation loop
  s.controller.initializeLoop()
  while not s.controller.isTerminateLoop():
  
    s.controller.startAnIteration()
    # Formula Execution Blocks
    try:
      # Column Formula_Column
      s.controller.startBlock('Formula_Column')
      Formula_Column = np.sin(DUMMY1_COLUMN)
      s.controller.endBlock()
      Formula_Column = s.coerceValues('Formula_Column', Formula_Column)
    except Exception as exc:
      s.controller.exceptionForBlock(exc)
     
    
    s.controller.endAnIteration()
    
  if s.controller.getException() is None:
    
    s.controller.startBlock('Epilogue')
    # Epilogue
    
    s.controller.endBlock()

except Exception as exc:
  s.controller.exceptionForBlock(exc)

if s.controller.getException() is not None:
  raise Exception(s.controller.formatError(is_absolute_linenumber=False))
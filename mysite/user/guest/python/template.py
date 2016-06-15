# Evaluation of the table MechaelisMenton.

    
from scisheets.core import api as api
# Uncomment the following to execute standalone
#
#_table = api.getTableFromFile('/home/ubuntu/SciSheets/mysite/user/guest/tables/mechaelis_menten_demo.pcl')
#_table.setNamespace(globals())
#s = api.APIFormulas(_table) 
#

from scisheets.plugins.roundValues import roundValues
from scisheets.plugins.slope import slope
from scisheets.plugins.intercept import intercept
s.assignColumnVariables([])
# Prologue
s.controller.startBlock("prologue")
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp
from numpy import nan  # Must follow sympy import 
s.controller.endBlock()


# Formulation evaluation loop
s.controller.initializeLoop()
while not s.controller.isTerminateIteration():
  s.controller.startAnIteration()

  try:
    
    # Formula Execution Blocks
    # Column INV_S
    s.controller.startBlock("INV_S")
    INV_S = roundValues(1/S,3)
    s.controller.endBlock()
    INV_S = s.coerceValues('INV_S', INV_S)
     
    # Column INV_V
    s.controller.startBlock("INV_V")
    INV_V = roundValues(1/V,3)
    s.controller.endBlock()
    INV_V = s.coerceValues('INV_V', INV_V)
     
    # Column INTERCEPT
    s.controller.startBlock("INTERCEPT")
    INTERCEPT = roundValues(intercept(INV_S,INV_V),3)
    s.controller.endBlock()
    INTERCEPT = s.coerceValues('INTERCEPT', INTERCEPT)
     
    # Column SLOPE
    s.controller.startBlock("SLOPE")
    SLOPE = roundValues(slope(INV_S, INV_V),3)
    s.controller.endBlock()
    SLOPE = s.coerceValues('SLOPE', SLOPE)
     
    # Column V_MAX
    s.controller.startBlock("V_MAX")
    V_MAX = roundValues(1/INTERCEPT,3)
    s.controller.endBlock()
    V_MAX = s.coerceValues('V_MAX', V_MAX)
     
    # Column K_M
    s.controller.startBlock("K_M")
    K_M = roundValues(SLOPE*V_MAX,3)
    s.controller.endBlock()
    K_M = s.coerceValues('K_M', K_M)
     
    pass
    
  except Exception as _error:
    s.controller.exceptionForBlock(_error)
  
  s.controller.endAnIteration() 
  
if s.controller.getException() is not None:
  # ProgramRunner calls s.controller.formatError()
  raise Exception(s.controller.getException())

# Epilogue
s.controller.startBlock("prologue")
s.controller.endBlock()
s.updateTableCellsAndColumnVariables([])


"""
ProgramRunner
1. If exception occurs,
  if s.controller.getException() is None:
    s.controller.exceptionForBlock()
  error = s.controller.formatError()
"""

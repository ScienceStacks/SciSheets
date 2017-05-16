# Export of the table MichaelisMenten

    

def michaelis(S, V):
  from scisheets.core import api as api
  s = api.APIPlugin('/home/ubuntu/SciSheets/mysite/user/guest/python/michaelis.scish')
  s.initialize()
  _table = s.getTable()
  
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
      # Column INV_S
      s.controller.startBlock('INV_S')
      INV_S = 1/S
      s.controller.endBlock()
      INV_S = s.coerceValues('INV_S', INV_S)
    except Exception as exc:
      s.controller.exceptionForBlock(exc)
     
    try:
      # Column INV_V
      s.controller.startBlock('INV_V')
      INV_V = np.round(1/V,2)
      s.controller.endBlock()
      INV_V = s.coerceValues('INV_V', INV_V)
    except Exception as exc:
      s.controller.exceptionForBlock(exc)
     
    try:
      # Column INTERCEPT
      s.controller.startBlock('INTERCEPT')
      import scipy.stats as ss
      SLOPE, INTERCEPT, _, _, _ = ss.linregress(INV_S, INV_V)
      SLOPE = np.round(SLOPE, 3)
      INTERCEPT = np.round(INTERCEPT, 3)
      s.controller.endBlock()
    except Exception as exc:
      s.controller.exceptionForBlock(exc)
     
    try:
      # Column V_MAX
      s.controller.startBlock('V_MAX')
      V_MAX = np.round(1/INTERCEPT,3)
      s.controller.endBlock()
      V_MAX = s.coerceValues('V_MAX', V_MAX)
    except Exception as exc:
      s.controller.exceptionForBlock(exc)
     
    try:
      # Column K_M
      s.controller.startBlock('K_M')
      K_M = np.round(SLOPE*V_MAX,3)
      s.controller.endBlock()
      K_M = s.coerceValues('K_M', K_M)
    except Exception as exc:
      s.controller.exceptionForBlock(exc)
     
    
    s.controller.endAnIteration()
    
  
  if s.controller.getException() is not None:
    raise Exception(s.controller.formatError(is_absolute_linenumber=True))
  
  s.controller.startBlock('Epilogue')
  # Epilogue
  
  s.controller.endBlock()
  
  return V_MAX,K_M

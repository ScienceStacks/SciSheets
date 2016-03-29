
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp
from sympy import *
from numpy import nan

    
from slope import slope
from intercept import intercept
def newMM(S,V):
  
  def convertToArray(arg):
    if isinstance(arg, np.ndarray):
      result = arg
    elif isinstance(arg, list):
      result = np.array(arg)
    else:
      result = np.array([arg])
    return result
  
  
  S = convertToArray(S)
  
  
  V = convertToArray(V)
  
  # Do initial assignments
  row = np.array(['1', '2', '3', '4', '5', '6'], dtype='|S1')
  INV_S = np.array([100.0, 20.0, 8.333333333333334, 5.0, 2.0, 1.0], dtype=float)
  INV_V = np.array([9.090909090909092, 5.2631578947368425, 4.761904761904762, 4.545454545454546, 4.761904761904762, 4.166666666666667], dtype=float)
  INTERCEPT = np.array([4.357398728502525, nan, nan, nan, nan, nan], dtype=float)
  SLOPE = np.array([0.04727827885497449, nan, nan, nan, nan, nan], dtype=float)
  V_MAX = np.array([0.2294947197415791, nan, nan, nan, nan, nan], dtype=float)
  K_M = np.array([0.010850115355686595, nan, nan, nan, nan, nan], dtype=float)
  #Evaluate the formulas
  for nn in range(1):
    try:
      INV_S = 1/S
      INV_V = 1/V
      INTERCEPT = intercept(INV_S, INV_V)
      SLOPE = slope(INV_S, INV_V)
      V_MAX = 1/INTERCEPT
      K_M=V_MAX*SLOPE
    except Exception as e:
      if nn == 0:
        raise Exception(e)
        break
  return V_MAX,K_M

from _compare_arrays import compareArrays
if __name__ == '__main__':
  S = np.array([0.01, 0.05, 0.12, 0.2, 0.5, 1.0], dtype=float)
  V = np.array([0.11, 0.19, 0.21, 0.22, 0.21, 0.24], dtype=float)
  V_MAX,K_M = newMM(S,V)
  b = True
  b = b and compareArrays(V_MAX, [0.2294947197415791, nan, nan, nan, nan, nan])
  b = b and compareArrays(K_M, [0.010850115355686595, nan, nan, nan, nan, nan])
  
  if b:
    print ('OK.')
  else:
    print ('Test failed.')
  

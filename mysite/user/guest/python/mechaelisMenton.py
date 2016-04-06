
import my_api as api
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp
from sympy import *
from numpy import nan  # Must follow sympy import
    
from slope import slope
from intercept import intercept

s = api.APIPlugin('/home/ubuntu/SciSheets/mysite/user/guest/tables/mechaelis_menton.pcl')
s.initialize()

def mechaelisMenton(S,V):
  
  # Assign column values to global variables
  row = s.getColumnValues('row')
  INV_S = s.getColumnValues('INV_S')
  INV_V = s.getColumnValues('INV_V')
  INTERCEPT = s.getColumnValues('INTERCEPT')
  SLOPE = s.getColumnValues('SLOPE')
  
  
  #Evaluate the formulas
  for nn in range(6):
    try:
      INV_S = 1/S
    except Exception as e:
      if nn == 5:
        raise Exception(e)
        break
    try:
      INV_V = 1/V
    except Exception as e:
      if nn == 5:
        raise Exception(e)
        break
    try:
      INTERCEPT = intercept(INV_S,INV_V)
    except Exception as e:
      if nn == 5:
        raise Exception(e)
        break
    try:
      SLOPE = slope(INV_S, INV_V)
    except Exception as e:
      if nn == 5:
        raise Exception(e)
        break
    try:
      V_MAX = 1/INTERCEPT
    except Exception as e:
      if nn == 5:
        raise Exception(e)
        break
    try:
      K_M = V_MAX*SLOPE
    except Exception as e:
      if nn == 5:
        raise Exception(e)
        break
  return V_MAX,K_M

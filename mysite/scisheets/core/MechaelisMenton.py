
# File generated as a SciSheets table export

    

from os import listdir
from os.path import isfile, join
import math as mt
import numpy as np
import pandas as pd
import scipy as sp
    
from slope import *
from intercept import *

def MechaelisMenton(THDPA,V):
  # Do initial assignments
  INV_THDPA = np.array([None, None, None, None, None, None], dtype=object)
  INV_V = np.array([None, None, None, None, None, None], dtype=object)
  INTERCEPT = np.array([None, None, None, None, None, None], dtype=object)
  SLOPE = np.array([None, None, None, None, None, None], dtype=object)
  Vmax = np.array([None, None, None, None, None, None], dtype=object)
  KM = np.array([None, None, None, None, None, None], dtype=object)
  for nn in range(6):
    try:
      INV_THDPA = 1/THDPA
    except Exception as e:
      if nn == 5:
        raise Exception(str(e))
        break
    try:
      INV_V = 1/V
    except Exception as e:
      if nn == 5:
        raise Exception(str(e))
        break
    try:
      INTERCEPT = intercept(INV_THDPA, INV_V)
    except Exception as e:
      if nn == 5:
        raise Exception(str(e))
        break
    try:
      SLOPE = slope(INV_THDPA, INV_V)
    except Exception as e:
      if nn == 5:
        raise Exception(str(e))
        break
    try:
      Vmax = 1/INTERCEPT
    except Exception as e:
      if nn == 5:
        raise Exception(str(e))
        break
    try:
      KM = Vmax*SLOPE
    except Exception as e:
      if nn == 5:
        print('error in formula Vmax*SLOPE: ' + str(e))
        break
  return Vmax, KM

if __name__ == '__main__':
  THDPA = np.array([0.01, 0.05, 0.12, 0.2, 0.5, 1.0], dtype=float)
  V = np.array([0.11, 0.19, 0.21, 0.22, 0.21, 0.24], dtype=float)
  print 'MechaelisMenton(THDPA,V)=' + str(MechaelisMenton(THDPA,V))

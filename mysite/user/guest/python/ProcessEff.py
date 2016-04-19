# Export of the table GeneTable

    
import my_api as api
import math as mt
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import scipy as sp
from sympy import *
from numpy import nan  # Must follow sympy import 

s = api.APIPlugin('/home/ubuntu/SciSheets/mysite/user/guest/tables/kristen_gene_table.pcl')
s.initialize()
def ProcessEff(EffData):
  # Assign column values to program variables.
  row = s.getColumnValues('row')
  BatchSize = s.getColumnValues('BatchSize')
  MinEff = s.getColumnValues('MinEff')
  MaxStd = s.getColumnValues('MaxStd')
  GroupedData = s.getColumnValues('GroupedData')
  GroupedPrunedData = s.getColumnValues('GroupedPrunedData')
  CensoredData = s.getColumnValues('CensoredData')
  # Evaluate the formulas.
  for nn in range(9):
    try:
      import random
      #EffData = [random.randint(50, 100) for x in range(15)]
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      batch_size = int(BatchSize[0])
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      min_eff = int(MinEff[0])
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      max_std = MaxStd[0]
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      # Grouping groups together samples based on BatchSize
      batch_count = len(EffData)/batch_size
      GroupedData = np.array(EffData).reshape(batch_count, batch_size)
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      # Pruning eliminates values less than MinEff
      GroupedPrunedData = []
      for data in GroupedData:
        new_data = []
        for d in data:
          if d >= min_eff:
            new_data.append(d)
        GroupedPrunedData.append(new_data)
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      #Eliminate Values if exceed MaxStd
      CensoredData = []
      for data in GroupedPrunedData:
        if (len(data) < 3) or (np.std(data) <= max_std):
          CensoredData.append(data)
        else:
          mean = np.average(data)
          distances = [np.abs(x - mean) for x in data]
          max_distance = np.max(distances)
          new_data = [x for x in data if np.abs(x - mean) < max_distance]
          CensoredData.append(new_data)
          
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      Mean = []
      for data in CensoredData:
        Mean.append(round(np.average(data),2))
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
    try:
      Std = []
      for data in CensoredData:
        Std.append(round(np.std(data),2))
    except Exception as e:
      if nn == 8:
        raise Exception(e)
        break
  
  return Mean,Std
''' 
  Example of a SciSheets user function. The input is one or more 
  numpy array. The output is a numpy array.
'''

import numpy as np


def timesTwo(input_array):
  """
     Multiples the input array times two.
  """
  return 2*input_array

if __name__ == "__main__":
  print ("Enter a list of numbers in square brackets (e.g., [1,2])")
  input_list = input()
  try:
    array = np.array(input_list)
    print ("Times two yields %s" % str(timesTwo(array)))
  except:
    print("Invalid input.")

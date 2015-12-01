'''Utility routines.'''

def ConvertType(v):
  # Converts to int, float, str as required
  # Input: v - string representation
  # Output: r - new representation
  try:
    r = int(v)
  except:
    try:
      r = float(v)
    except:
      r = v  # Leave as string
  return r

def ConvertTypes(values):
  # Converts a list strings to a list of their types
  # Input: values - list
  # Output: results
  results = []
  for v in values:
    results.append(ConvertType(v))
  return results

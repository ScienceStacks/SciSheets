'''Utility routines.'''

import random
import string

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

def randomWords(count, size=5):
  # Generates a sequence of random words of the same size
  # Input: count - number of random words generated
  #        size - size of each word
  # Output: result - list of random words
  return [randomWord(size=size) for n in range(count)]

def randomWord(size=5):
  # Generates a random word
  # Input: size - size of each word
  # Output: word
  word = ''
  for n in range(size):
    word += random.choice(string.letters)
  return word


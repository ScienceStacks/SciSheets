'''Utility routines.'''

import random
import string
import os

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

# TODO: Add tests
def stringToClass(cls_str):
  """
  Converts the string representation of a class to a class object.
  :param str cls_str: string representation of a class
  :return type class:
  """
  import_stg1 = cls_str.split(" ")[1]
  import_stg2 = import_stg1.replace("'", "")
  import_stg3 = import_stg2.replace(">", "")
  import_parse = import_stg3.split(".")
  cls = import_parse[-1]
  import_path = '.'.join(import_parse[:-1])
  import_statement = "from %s import %s" % (import_path, cls)
  exec(import_statement)
  assign_statement = "this_class = %s" % cls
  exec(assign_statement)
  return this_class

def getFileExtension(filepath):
  """
  :param str filepath:
  :return str: extension excluding the "."
  """
  extension = os.path.split(filepath)[-1]
  split_filename = extension.split('.')
  if len(split_filename) == 1:
    ext = None
  else:
    ext = split_filename[-1]
  return ext

def stripFileExtension(filepath):
  """
  :param str filepath:
  :return str:
 filepath without the extension
  """
  split_filepath = list(os.path.split(filepath))
  filename = split_filepath[-1]
  split_filename = filename.split('.')
  stripped_filename = split_filename[0]
  split_filepath[-1] = stripped_filename
  fullpath = ""
  for ele in split_filepath:
    fullpath = os.path.join(fullpath, ele)
  return fullpath

def changeFileExtension(filepath, extension):
  """
  :param str filepath:
  :param str extension: without "."
  :return str: filepath without the extension
  """
  stripped_filepath = stripFileExtension(filepath)
  if extension is None:
    return "%s" % stripped_filepath
  else:
    return "%s.%s" % (stripped_filepath, extension)

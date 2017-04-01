"""
Utility to change the extension of a file
"""

from mysite.helpers.util import changeFileExtension, getFileExtension
import os

CUR_EXT = "sci"
NEW_EXT = "scish"

files = [ff for ff in os.listdir(".")  \
         if getFileExtension(ff) == CUR_EXT]
for ff in files:
  new_file = changeFileExtension(ff, NEW_EXT)
  os.rename(ff, new_file)

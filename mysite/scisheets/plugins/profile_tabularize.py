""" Profile for tabularize """

import profile


# Set up the API

# Do the profile
cmd = '''
from scisheets.plugins.tabularize import tabularize
from scisheets.core.helpers.api_util import getTableFromFile
from mysite import settings
from scisheets.core.api import APIFormulas
import os
FILEPATH = os.path.join(settings.SCISHEETS_TEST_DIR, "test_tabularize_1.pcl")
table = getTableFromFile(FILEPATH, verify=False)
s = APIFormulas(table) 
for n in range(10):
  _ = tabularize(s, 'Groups', 1, 'MeanCt', 
               new_category_colnm='BioRuns',
               values_colnm_prefix='Gene_')
print'''
profile.run(cmd)


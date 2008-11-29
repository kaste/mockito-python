# to be implemented - copy contents of MockitoDemoTest into the README

import os
import re

def openFile(f, m='r'):
  if (os.path.exists(f)):
    return open(f, m)
  else:
    return open('../' + f, m)
    
demo_test = '  '.join(openFile('mockito/mockito_demo_test.py').readlines())
demo_test = re.compile('if __name__.*', re.S).sub('', demo_test)

readme_before = ''.join(openFile('README').readlines())
readme_after = re.compile('import unittest.*(?=\nFor more info)', re.S).sub(demo_test, readme_before)

if (readme_before != readme_after):
  print "Writing README..."
  readme_file = openFile('README', 'w')
  readme_file.write(readme_after)
else:
  print "Writing README not required" 
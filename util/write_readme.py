# to be implemented - copy contents of MockitoDemoTest into the README

import os
import re

def openFile(f, m='r'):
  if (os.path.exists(f)):
    return open(f, m)
  else:
    return open('../' + f, m)
    
demo_test = '  '.join(openFile('src/mockito_demo_test.py').readlines())
demo_test = re.compile('#end.*', re.S).sub('', demo_test)

readme = ''.join(openFile('README').readlines())
readme = re.compile('import unittest.*(?=For more info)', re.S).sub(demo_test, readme)

#todo check if readme changed - if not then do not write
readme_file = openFile('README', 'w')
readme_file.write(readme)
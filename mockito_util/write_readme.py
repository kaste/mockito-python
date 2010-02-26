import os
import re

def openFile(f, m='r'):
  if (os.path.exists(f)):
    return open(f, m)
  else:
    return open('../' + f, m)
    
demo_test = '  '.join(openFile('mockito_test/demo_test.py').readlines())
demo_test = demo_test.split('#DELIMINATOR')[1]

readme_before = ''.join(openFile('README').readlines())
token = 'Basic usage:'
readme_after = re.compile(token + '.*', re.S).sub(token + '\n' + demo_test, readme_before)

if (readme_before != readme_after):  
  readme_file = openFile('README', 'w')
  readme_file.write(readme_after)
  print "README updated"
else:
  print "README update not required" 

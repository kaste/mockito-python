import unittest
import sys, os
import re

def run():
  if '--quiet' in sys.argv:
      verbosity_level = 1
  else:
      verbosity_level = 2
        
  pattern = re.compile('([a-z]+_)+test\.py$')

  loader = unittest.TestLoader()
  suite = unittest.TestSuite()
  
  names = [f.replace('.py', '') for f in os.listdir('.') if pattern.match(f, 1)]
  for name in names: 
    suite.addTests(loader.loadTestsFromName(name))
  unittest.TextTestRunner(verbosity=verbosity_level).run(suite)


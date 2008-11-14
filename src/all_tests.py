import unittest
import os
import re

pattern = re.compile('([a-z]+_)+test\.py$')

loader = unittest.TestLoader()
suite = unittest.TestSuite()

names = [f.replace('.py', '') for f in os.listdir('.') if pattern.match(f, 1)]   
for name in names: suite.addTests(loader.loadTestsFromName(name))
unittest.TextTestRunner(verbosity=2).run(suite)
#!/usr/bin/env python
# coding: utf-8

from unittest import TestLoader as BaseTestLoader, TestSuite

class TestLoader(BaseTestLoader):
  def __init__(self):
    BaseTestLoader.__init__(self)

  def loadTestsFromNames(self, names, module):
    suite = TestSuite()
    for test in findTests(dirs=names):
      suite.addTests(super(TestLoader, self).loadTestsFromName(test))
    return suite

def findTests(dirs):
  import os, re
  pattern = re.compile('([a-z]+_)+test\.py$')
  for dir in dirs:
    for fileName in os.listdir(dir):
      if pattern.match(fileName):
        yield os.path.join(dir, fileName).replace('.py', '').replace(os.sep, '.')


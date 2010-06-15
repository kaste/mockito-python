#!/usr/bin/env python
# coding: utf-8

from unittest import TestLoader as BaseTestLoader, TestSuite
import sys

class TestLoader(BaseTestLoader):
  def __init__(self):
    BaseTestLoader.__init__(self)

  def loadTestsFromName(self, name, module=None):
    suite = TestSuite()
    for test in findTests(name):
      sys.path.insert(0, name) # python3 compatibility
      suite.addTests(super(TestLoader, self).loadTestsFromName(test))
      del sys.path[0] # python3 compatibility
    return suite

  def loadTestsFromNames(self, names, module=None):
    suite = TestSuite()
    for name in names:
      suite.addTests(self.loadTestsFromName(name))
    return suite

def findTests(dir):
  import os, re
  pattern = re.compile('([a-z]+_)+test\.py$')
  for fileName in os.listdir(dir):
    if pattern.match(fileName):
      yield os.path.join(dir, fileName).replace('.py', '').replace(os.sep, '.')

__all__ = [TestLoader]


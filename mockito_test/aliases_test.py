#!/usr/bin/env python
# coding: utf-8

from test_base import TestBase
from mockito import mock, Mock
import warnings

class AliasesTest(TestBase):
  def testMockCreationAlias(self):
      warnings.simplefilter("ignore")      
      self.assertTrue(isinstance(Mock(), mock))
  
if __name__ == '__main__':
    import unittest    
    unittest.main()

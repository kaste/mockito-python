#!/usr/bin/env python
# coding: utf-8

from test_base import TestBase
from mockito import mock, Mock

class AliasesTest(TestBase):
  def testMockCreationAlias(self):
    self.assertEquals(mock, Mock)
  
if __name__ == '__main__':    
    unittest.main()

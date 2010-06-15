#!/usr/bin/env python
# coding: utf-8

import mockito_util.write_readme

#all below code will be merged with README
#DELIMINATOR
import unittest
from mockito import mock, when, verify

class DemoTest(unittest.TestCase):
  def testStubbing(self):
    # create a mock
    ourMock = mock()

    # stub it
    when(ourMock).getStuff("cool").thenReturn("cool stuff")
    
    # use the mock
    self.assertEqual("cool stuff", ourMock.getStuff("cool"))
    
    # what happens when you pass different argument?
    self.assertEqual(None, ourMock.getStuff("different argument"))
    
  def testVerification(self):
    # create a mock
    theMock = mock()

    # use the mock
    theMock.doStuff("cool")
    
    # verify the interactions. Method and parameters must match. Otherwise verification error.
    verify(theMock).doStuff("cool")
  
#DELIMINATOR
#all above code will be merged with README
if __name__ == '__main__':    
    unittest.main()    


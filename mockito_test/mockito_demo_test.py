import test_base
import util.write_readme

#all below code will be merged with README
#DELIMINATOR
import unittest
from mockito import *

class MockitoDemoTest(unittest.TestCase):

  def testStubbing(self):
    # create a mock
    mock = Mock()

    # stub it
    when(mock).getStuff("cool").thenReturn("cool stuff")
    
    # use the mock
    self.assertEqual("cool stuff", mock.getStuff("cool"))
    
    # what happens when you pass different argument?
    self.assertEqual(None, mock.getStuff("different argument"))
    
  def testVerification(self):
    # create a mock
    mock = Mock()

    # use the mock
    mock.doStuff("cool")
    
    # verify the interactions. Method and parameters must match. Otherwise verification error.
    verify(mock).doStuff("cool")
  
#DELIMINATOR
#all above code will be merged with README
if __name__ == '__main__':    
    unittest.main()    
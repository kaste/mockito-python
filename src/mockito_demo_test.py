import unittest
from mockito import *

#Add all stuff that is implemented but not documented
class MockitoDemoTest(unittest.TestCase):

  def testStubbing(self):
    # create a mock
    mock = Mock()

    # stub it
    when(mock).getStuff().thenReturn("stuff")
    
    # use the mock
    self.assertEqual("stuff", mock.getStuff())
    
  def testVerification(self):
    # create a mock
    mock = Mock()

    # use the mock
    mock.doStuff()
    
    # verify the interactions
    verify(mock).doStuff()

if __name__ == '__main__': unittest.main()
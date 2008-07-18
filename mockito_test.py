import unittest
from mockito import * 

class MockitoTest(unittest.TestCase):
  
  def testVerifies(self):
    mock = Mock()
    mock.foo()
    mock.someOtherMethod(1, "foo", "bar")

    verify(mock).foo()
    verify(mock).someOtherMethod(1, "foo", "bar")
    
  def testFailsVerification(self):
    mock = Mock()
    mock.foo("boo")

    try:
      verify(mock).foo("ah")
      self.fail
    except VerificationError:
      pass
    
  def testVerifiesMultipleCalls(self):
    mock = Mock()
    mock.foo()
    mock.foo()
    mock.foo()

    verify(mock, times(3)).foo()
    
  def testFailsVerificationOfMultipleCalls(self):
    mock = Mock()
    mock.foo()
    mock.foo()
    mock.foo()
    
    try:
      verify(mock, times(2)).foo()
      self.fail
    except VerificationError:
      pass
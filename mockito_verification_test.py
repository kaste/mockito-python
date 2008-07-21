from test_base import *
from mockito import *

class MockitoTest(TestBase):
  
  def testVerifies(self):
    mock = Mock()
    mock.foo()
    mock.someOtherMethod(1, "foo", "bar")

    verify(mock).foo()
    verify(mock).someOtherMethod(1, "foo", "bar")

  def testVerifiesWhenMethodIsUsingKeywordArguments(self):
    mock = Mock()
    mock.foo()
    mock.someOtherMethod(1, fooarg="foo", bararg="bar")

    verify(mock).foo()
    verify(mock).someOtherMethod(1, bararg="bar", fooarg="foo")

  def testFailsVerification(self):
    mock = Mock()
    mock.foo("boo")

    self.assertRaises(VerificationError, verify(mock).foo, "not boo")

  def testVerifiesAnyTimes(self):
    mock = Mock()
    mock.foo()
    
    verify(mock).foo()
    verify(mock).foo()
    verify(mock).foo()
    
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
    
    self.assertRaises(VerificationError, verify(mock, times(2)).foo)
    
  def testVerifiesNoMoreInteractions(self):
    mock, mockTwo = Mock(), Mock()
    mock.foo()
    
    verify(mock).foo()
    verifyNoMoreInteractions(mock, mockTwo)    
    
  def testFailsNoMoreInteractions(self):
    mock = Mock()
    mock.foo()
    
    self.assertRaises(VerificationError, verifyNoMoreInteractions, mock)

from test_base import *
from mockito import *

#TODO remove Mockito prefix from all classes
class MockitoVerificationTest(TestBase):
  
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

  def testVerifiesUsingAnyMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    verify(mock).foo(1, any())
    verify(mock).foo(any(), "bar")
    verify(mock).foo(any(), any())

  def testVerifiesUsingAnyIntMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    verify(mock).foo(any(int), "bar")

  def testFailsVerificationUsingAnyIntMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    self.assertRaises(VerificationError, verify(mock).foo, 1, any(int))
    self.assertRaises(VerificationError, verify(mock).foo, any(int))
    
  def testNumberOfTimesDefinedDirectlyInVerify(self):
    mock = Mock()
    mock.foo("bar")
    
    verify(mock, times=1).foo("bar")

  def testFailsWhenTimesIsLessThanZero(self):
    self.assertRaises(ArgumentError, verify, None, -1)

if __name__ == '__main__':
  unittest.main()
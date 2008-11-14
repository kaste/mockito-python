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
    mockTwo.bar()
    
    verify(mock).foo()
    verify(mockTwo).bar()
    verifyNoMoreInteractions(mock, mockTwo)    
    
  def testFailsNoMoreInteractions(self):
    mock = Mock()
    mock.foo()
    
    self.assertRaises(VerificationError, verifyNoMoreInteractions, mock)
    
  def testVerifiesZeroInteractions(self):
    mock = Mock()
    verifyZeroInteractions(mock)
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

  def testVerifiesAtLeastTwoWhenMethodInvokedTwice(self):
    mock = Mock()
    mock.foo()
    mock.foo()

    verify(mock, atLeast=2).foo()

  def testVerifiesAtLeastTwoWhenMethodInvokedFourTimes(self):
    mock = Mock()
    mock.foo()
    mock.foo()
    mock.foo()
    mock.foo()

    verify(mock, atLeast=2).foo()

  def testFailsWhenMethodInvokedOnceForAtLeastTwoVerification(self):
    mock = Mock()
    mock.foo()

    self.assertRaises(VerificationError, verify(mock, atLeast=2).foo)

  def testVerifiesAtMostTwoWhenMethodInvokedTwice(self):
    mock = Mock()
    mock.foo()
    mock.foo()

    verify(mock, atMost=2).foo()

  def testVerifiesAtMostTwoWhenMethodInvokedOnce(self):
    mock = Mock()
    mock.foo()

    verify(mock, atMost=2).foo()

  def testFailsWhenMethodInvokedFourTimesForAtMostTwoVerification(self):
    mock = Mock()
    mock.foo()
    mock.foo()
    mock.foo()
    mock.foo()

    self.assertRaises(VerificationError, verify(mock, atMost=2).foo)

  def testVerifiesBetween(self):
    mock = Mock()
    mock.foo()
    mock.foo()

    verify(mock, between=[1, 2]).foo()
    verify(mock, between=[2, 3]).foo()
    verify(mock, between=[1, 5]).foo()
    verify(mock, between=[2, 2]).foo()

  def testFailsVerificationWithBetween(self):
    mock = Mock()
    mock.foo()
    mock.foo()
    mock.foo()

    self.assertRaises(VerificationError, verify(mock, between=[1, 2]).foo)
    self.assertRaises(VerificationError, verify(mock, between=[4, 9]).foo)

  def testFailsAtMostAtLeastAndBetweenVerificationWithWrongArguments(self):
    mock = Mock()
    
    self.assertRaises(ArgumentError, verify, mock, atLeast=0)
    self.assertRaises(ArgumentError, verify, mock, atLeast=-5)
    self.assertRaises(ArgumentError, verify, mock, atMost=0)
    self.assertRaises(ArgumentError, verify, mock, atMost=-5)
    self.assertRaises(ArgumentError, verify, mock, between=[5, 1])
    self.assertRaises(ArgumentError, verify, mock, between=[-1, 1])
    self.assertRaises(ArgumentError, verify, mock, atLeast=5, atMost=5)
    self.assertRaises(ArgumentError, verify, mock, atLeast=5, between=[1, 2])
    self.assertRaises(ArgumentError, verify, mock, atMost=5, between=[1, 2])    
    self.assertRaises(ArgumentError, verify, mock, atLeast=5, atMost=5, between=[1, 2])
    
if __name__ == '__main__':
  unittest.main()
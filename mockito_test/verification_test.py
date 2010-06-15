import test_base
from mockito import *

class VerificationTest(test_base.TestBase):
  
  def testVerifies(self):
    theMock = mock()
    theMock.foo()
    theMock.someOtherMethod(1, "foo", "bar")

    verify(theMock).foo()
    verify(theMock).someOtherMethod(1, "foo", "bar")

  def testVerifiesWhenMethodIsUsingKeywordArguments(self):
    theMock = mock()
    theMock.foo()
    theMock.someOtherMethod(1, fooarg="foo", bararg="bar")

    verify(theMock).foo()
    verify(theMock).someOtherMethod(1, bararg="bar", fooarg="foo")
    
  def testVerifiesDetectsNamedArguments(self):
    theMock = mock()
    theMock.foo(fooarg="foo", bararg="bar")

    verify(theMock).foo(bararg="bar", fooarg="foo") 
    try:    
      verify(theMock).foo(bararg="foo", fooarg="bar")
      self.fail();
    except VerificationError:
      pass                         
    
  def testFailsVerification(self):
    theMock = mock()
    theMock.foo("boo")

    self.assertRaises(VerificationError, verify(theMock).foo, "not boo")

  def testVerifiesAnyTimes(self):
    theMock = mock()
    theMock.foo()
    
    verify(theMock).foo()
    verify(theMock).foo()
    verify(theMock).foo()
    
  def testVerifiesMultipleCalls(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()
    theMock.foo()

    verify(theMock, times(3)).foo()
    
  def testFailsVerificationOfMultipleCalls(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()
    theMock.foo()
    
    self.assertRaises(VerificationError, verify(theMock, times(2)).foo)
    
  def testVerifiesNoMoreInteractions(self):
    mockOne, mockTwo = mock(), mock()
    mockOne.foo()
    mockTwo.bar()
    
    verify(mockOne).foo()
    verify(mockTwo).bar()
    verifyNoMoreInteractions(mockOne, mockTwo)    
    
  def testFailsNoMoreInteractions(self):
    theMock = mock()
    theMock.foo()
    
    self.assertRaises(VerificationError, verifyNoMoreInteractions, theMock)
    
  def testVerifiesZeroInteractions(self):
    theMock = mock()
    verifyZeroInteractions(theMock)
    theMock.foo()
    
    self.assertRaises(VerificationError, verifyNoMoreInteractions, theMock)    

  def testVerifiesUsingAnyMatcher(self):
    theMock = mock()
    theMock.foo(1, "bar")
    
    verify(theMock).foo(1, any())
    verify(theMock).foo(any(), "bar")
    verify(theMock).foo(any(), any())

  def testVerifiesUsingAnyIntMatcher(self):
    theMock = mock()
    theMock.foo(1, "bar")
    
    verify(theMock).foo(any(int), "bar")

  def testFailsVerificationUsingAnyIntMatcher(self):
    theMock = mock()
    theMock.foo(1, "bar")
    
    self.assertRaises(VerificationError, verify(theMock).foo, 1, any(int))
    self.assertRaises(VerificationError, verify(theMock).foo, any(int))
    
  def testNumberOfTimesDefinedDirectlyInVerify(self):
    theMock = mock()
    theMock.foo("bar")
    
    verify(theMock, times=1).foo("bar")

  def testFailsWhenTimesIsLessThanZero(self):
    self.assertRaises(ArgumentError, verify, None, -1)

  def testVerifiesAtLeastTwoWhenMethodInvokedTwice(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()

    verify(theMock, atleast=2).foo()

  def testVerifiesAtLeastTwoWhenMethodInvokedFourTimes(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()
    theMock.foo()
    theMock.foo()

    verify(theMock, atleast=2).foo()

  def testFailsWhenMethodInvokedOnceForAtLeastTwoVerification(self):
    theMock = mock()
    theMock.foo()
    self.assertRaises(VerificationError, verify(theMock, atleast=2).foo)

  def testVerifiesAtMostTwoWhenMethodInvokedTwice(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()

    verify(theMock, atmost=2).foo()

  def testVerifiesAtMostTwoWhenMethodInvokedOnce(self):
    theMock = mock()
    theMock.foo()

    verify(theMock, atmost=2).foo()

  def testFailsWhenMethodInvokedFourTimesForAtMostTwoVerification(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()
    theMock.foo()
    theMock.foo()

    self.assertRaises(VerificationError, verify(theMock, atmost=2).foo)

  def testVerifiesBetween(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()

    verify(theMock, between=[1, 2]).foo()
    verify(theMock, between=[2, 3]).foo()
    verify(theMock, between=[1, 5]).foo()
    verify(theMock, between=[2, 2]).foo()

  def testFailsVerificationWithBetween(self):
    theMock = mock()
    theMock.foo()
    theMock.foo()
    theMock.foo()

    self.assertRaises(VerificationError, verify(theMock, between=[1, 2]).foo)
    self.assertRaises(VerificationError, verify(theMock, between=[4, 9]).foo)

  def testFailsAtMostAtLeastAndBetweenVerificationWithWrongArguments(self):
    theMock = mock()
    
    self.assertRaises(ArgumentError, verify, theMock, atleast=0)
    self.assertRaises(ArgumentError, verify, theMock, atleast=-5)
    self.assertRaises(ArgumentError, verify, theMock, atmost=0)
    self.assertRaises(ArgumentError, verify, theMock, atmost=-5)
    self.assertRaises(ArgumentError, verify, theMock, between=[5, 1])
    self.assertRaises(ArgumentError, verify, theMock, between=[-1, 1])
    self.assertRaises(ArgumentError, verify, theMock, atleast=5, atmost=5)
    self.assertRaises(ArgumentError, verify, theMock, atleast=5, between=[1, 2])
    self.assertRaises(ArgumentError, verify, theMock, atmost=5, between=[1, 2])    
    self.assertRaises(ArgumentError, verify, theMock, atleast=5, atmost=5, between=[1, 2])
    
if __name__ == '__main__':
  test_base.unittest.main()

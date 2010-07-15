#!/usr/bin/env python
# coding: utf-8

from test_base import TestBase, main
from mockito import mock, verify, inorder, VerificationError , ArgumentError, verifyNoMoreInteractions, verifyZeroInteractions, any
from mockito.verification import never
      
class VerificationTestBase(TestBase):
  def __init__(self, verification_function, *args, **kwargs):
    self.verification_function = verification_function
    TestBase.__init__(self, *args, **kwargs)
    
  def setUp(self):
    self.mock = mock()
  
  def testVerifies(self):
    self.mock.foo()
    self.mock.someOtherMethod(1, "foo", "bar")

    self.verification_function(self.mock).foo()
    self.verification_function(self.mock).someOtherMethod(1, "foo", "bar")

  def testVerifiesWhenMethodIsUsingKeywordArguments(self):
    self.mock.foo()
    self.mock.someOtherMethod(1, fooarg="foo", bararg="bar")

    self.verification_function(self.mock).foo()
    self.verification_function(self.mock).someOtherMethod(1, bararg="bar", fooarg="foo")
    
  def testVerifiesDetectsNamedArguments(self):
    self.mock.foo(fooarg="foo", bararg="bar")

    self.verification_function(self.mock).foo(bararg="bar", fooarg="foo") 
    try:    
      self.verification_function(self.mock).foo(bararg="foo", fooarg="bar")
      self.fail();
    except VerificationError:
      pass                         
    
  def testFailsVerification(self):
    self.mock.foo("boo")

    self.assertRaises(VerificationError, self.verification_function(self.mock).foo, "not boo")

  def testVerifiesAnyTimes(self):
    self.mock = mock()
    self.mock.foo()
    
    self.verification_function(self.mock).foo()
    self.verification_function(self.mock).foo()
    self.verification_function(self.mock).foo()
    
  def testVerifiesMultipleCalls(self):
    self.mock = mock()
    self.mock.foo()
    self.mock.foo()
    self.mock.foo()

    self.verification_function(self.mock, times=3).foo()
    
  def testFailsVerificationOfMultipleCalls(self):
    self.mock = mock()
    self.mock.foo()
    self.mock.foo()
    self.mock.foo()
    
    self.assertRaises(VerificationError, self.verification_function(self.mock, times=2).foo) 

  def testVerifiesUsingAnyMatcher(self):
    self.mock.foo(1, "bar")
    
    self.verification_function(self.mock).foo(1, any())
    self.verification_function(self.mock).foo(any(), "bar")
    self.verification_function(self.mock).foo(any(), any())

  def testVerifiesUsingAnyIntMatcher(self):
    self.mock.foo(1, "bar")
    
    self.verification_function(self.mock).foo(any(int), "bar")

  def testFailsVerificationUsingAnyIntMatcher(self):
    self.mock.foo(1, "bar")
    
    self.assertRaises(VerificationError, self.verification_function(self.mock).foo, 1, any(int))
    self.assertRaises(VerificationError, self.verification_function(self.mock).foo, any(int))
    
  def testNumberOfTimesDefinedDirectlyInVerify(self):
    self.mock.foo("bar")
    
    self.verification_function(self.mock, times=1).foo("bar")

  def testFailsWhenTimesIsLessThanZero(self):
    self.assertRaises(ArgumentError, self.verification_function, None, -1)

  def testVerifiesAtLeastTwoWhenMethodInvokedTwice(self):
    self.mock.foo()
    self.mock.foo()

    self.verification_function(self.mock, atleast=2).foo()

  def testVerifiesAtLeastTwoWhenMethodInvokedFourTimes(self):
    self.mock.foo()
    self.mock.foo()
    self.mock.foo()
    self.mock.foo()

    self.verification_function(self.mock, atleast=2).foo()

  def testFailsWhenMethodInvokedOnceForAtLeastTwoVerification(self):
    self.mock.foo()
    self.assertRaises(VerificationError, self.verification_function(self.mock, atleast=2).foo)

  def testVerifiesAtMostTwoWhenMethodInvokedTwice(self):
    self.mock.foo()
    self.mock.foo()

    self.verification_function(self.mock, atmost=2).foo()

  def testVerifiesAtMostTwoWhenMethodInvokedOnce(self):
    self.mock.foo()

    self.verification_function(self.mock, atmost=2).foo()

  def testFailsWhenMethodInvokedFourTimesForAtMostTwoVerification(self):
    self.mock.foo()
    self.mock.foo()
    self.mock.foo()
    self.mock.foo()

    self.assertRaises(VerificationError, self.verification_function(self.mock, atmost=2).foo)

  def testVerifiesBetween(self):
    self.mock.foo()
    self.mock.foo()

    self.verification_function(self.mock, between=[1, 2]).foo()
    self.verification_function(self.mock, between=[2, 3]).foo()
    self.verification_function(self.mock, between=[1, 5]).foo()
    self.verification_function(self.mock, between=[2, 2]).foo()

  def testFailsVerificationWithBetween(self):
    self.mock.foo()
    self.mock.foo()
    self.mock.foo()

    self.assertRaises(VerificationError, self.verification_function(self.mock, between=[1, 2]).foo)
    self.assertRaises(VerificationError, self.verification_function(self.mock, between=[4, 9]).foo)

  def testFailsAtMostAtLeastAndBetweenVerificationWithWrongArguments(self):   
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atleast=0)
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atleast=-5)
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atmost=0)
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atmost=-5)
    self.assertRaises(ArgumentError, self.verification_function, self.mock, between=[5, 1])
    self.assertRaises(ArgumentError, self.verification_function, self.mock, between=[-1, 1])
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atleast=5, atmost=5)
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atleast=5, between=[1, 2])
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atmost=5, between=[1, 2])    
    self.assertRaises(ArgumentError, self.verification_function, self.mock, atleast=5, atmost=5, between=[1, 2])
    
  def runTest(self):
    pass

class VerifyTest(VerificationTestBase):
  def __init__(self, *args, **kwargs):
    VerificationTestBase.__init__(self, verify, *args, **kwargs)
    
  def testVerifyNeverCalled(self):
    verify(self.mock, never).someMethod()
    
  def testVerifyNeverCalledRaisesError(self):
    self.mock.foo()
    self.assertRaises(VerificationError, verify(self.mock, never).foo)

class InorderVerifyTest(VerificationTestBase):
  def __init__(self, *args, **kwargs):
    VerificationTestBase.__init__(self, inorder.verify, *args, **kwargs)
        
  def setUp(self):
    self.mock = mock()

  def testPassesIfOneIteraction(self):
    self.mock.first()    
    inorder.verify(self.mock).first()
 
  def testPassesIfMultipleInteractions(self):
    self.mock.first()
    self.mock.second()
    self.mock.third()
    
    inorder.verify(self.mock).first()
    inorder.verify(self.mock).second()
    inorder.verify(self.mock).third()
    
  def testFailsIfNoInteractions(self):
    self.assertRaises(VerificationError, inorder.verify(self.mock).first)
    
  def testFailsIfWrongOrderOfInteractions(self):
    self.mock.first()
    self.mock.second()
    
    self.assertRaises(VerificationError, inorder.verify(self.mock).second) 

  def testErrorMessage(self):
    self.mock.second()
    self.mock.first()
    self.assertRaisesMessage("\nWanted first() to be invoked, got second() instead", inorder.verify(self.mock).first)
    

  def testPassesMixedVerifications(self):
    self.mock.first()
    self.mock.second()

    verify(self.mock).first()
    verify(self.mock).second()

    inorder.verify(self.mock).first()
    inorder.verify(self.mock).second()

  def testFailsMixedVerifications(self):
    self.mock.second()
    self.mock.first()
    
    # first - normal verifications, they should pass
    verify(self.mock).first()
    verify(self.mock).second()

    # but, inorder verification should fail
    self.assertRaises(VerificationError, inorder.verify(self.mock).first)


class VerifyNoMoreInteractionsTest(TestBase):
  def testVerifies(self):
    mockOne, mockTwo = mock(), mock()
    mockOne.foo()
    mockTwo.bar()
    
    verify(mockOne).foo()
    verify(mockTwo).bar()
    verifyNoMoreInteractions(mockOne, mockTwo)    
    
  def testFails(self):
    theMock = mock()
    theMock.foo()   
    self.assertRaises(VerificationError, verifyNoMoreInteractions, theMock)
    

class VerifyZeroInteractionsTest(TestBase):
    def testVerifies(self):
      theMock = mock()
      verifyZeroInteractions(theMock)
      theMock.foo()      
      self.assertRaises(VerificationError, verifyNoMoreInteractions, theMock)
    
    
if __name__ == '__main__':
  main()


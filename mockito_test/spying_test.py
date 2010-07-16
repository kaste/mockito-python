#!/usr/bin/env python
# coding: utf-8

from mockito_test.test_base import TestBase
from mockito import spy, verify, VerificationError

class Dummy:
  def foo(self):
    return "foo"
  
  def bar(self):
    raise TypeError
  
  def return_args(self, *args, **kwargs):
    return (args, kwargs)

class SpyingTest(TestBase):
  def testPreservesReturnValues(self):
    dummy = Dummy()
    spiedDummy = spy(dummy)
    self.assertEquals(dummy.foo(), spiedDummy.foo())
    
  def testPreservesSideEffects(self):
    dummy = spy(Dummy())
    self.assertRaises(TypeError, dummy.bar)
    
  def testPassesArgumentsCorrectly(self):
    dummy = spy(Dummy())
    self.assertEquals((('foo', 1), {'bar': 'baz'}), dummy.return_args('foo', 1, bar='baz'))
    
  def testIsVerifiable(self):
    dummy = spy(Dummy())
    dummy.foo()
    verify(dummy).foo()
    self.assertRaises(VerificationError, verify(dummy).bar)
    
  def testRaisesAttributeErrorIfNoSuchMethod(self):
    dummy = spy(Dummy())
    try:
      dummy.lol()
      self.fail("Should fail if no such method.")
    except AttributeError, e:
      self.assertEquals("You tried to call method 'lol' which 'Dummy' instance does not have.", str(e))
      
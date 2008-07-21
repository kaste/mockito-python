from test_base import *
from mockito import *

class MockitoTest(TestBase):
  
  def testVerifiesUsingAnyMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    verify(mock).foo(1, any)
    verify(mock).foo(any, "bar")
    verify(mock).foo(any, any)

  def testVerifiesUsingAnyIntMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    verify(mock).foo(anyInt, "bar")

  def testFailsVerificationUsingAnyIntMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    self.assertRaises(VerificationError, verify(mock).foo, 1, anyInt)
    self.assertRaises(VerificationError, verify(mock).foo, anyInt)

  def testVerifiesUsingAnyStrMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    verify(mock).foo(1, anyStr)

  def testFailsVerificationUsingAnyStrMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    self.assertRaises(VerificationError, verify(mock).foo, anyStr, 1)
    self.assertRaises(VerificationError, verify(mock).foo, anyStr)

  def testVerifiesUsingAnyFloatMatcher(self):
    mock = Mock()
    mock.foo(1.1, "bar")
    
    verify(mock).foo(anyFloat, "bar")

  def testFailsVerificationUsingAnyFloatMatcher(self):
    mock = Mock()
    mock.foo(1.1, "bar")
    
    self.assertRaises(VerificationError, verify(mock).foo, anyFloat, anyFloat)
    self.assertRaises(VerificationError, verify(mock).foo, anyFloat)
    self.assertRaises(VerificationError, verify(mock).foo, 1.1, anyFloat)

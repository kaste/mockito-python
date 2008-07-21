from test_base import *
from mockito import *

class MockitoTest(TestBase):
  
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

  def testVerifiesUsingAnyStrMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    verify(mock).foo(1, any(str))

  def testFailsVerificationUsingAnyStrMatcher(self):
    mock = Mock()
    mock.foo(1, "bar")
    
    self.assertRaises(VerificationError, verify(mock).foo, any(str), 1)
    self.assertRaises(VerificationError, verify(mock).foo, any(str))

  def testVerifiesUsingAnyFloatMatcher(self):
    mock = Mock()
    mock.foo(1.1, "bar")
    
    verify(mock).foo(any(float), "bar")

  def testFailsVerificationUsingAnyFloatMatcher(self):
    mock = Mock()
    mock.foo(1.1, "bar")
    
    self.assertRaises(VerificationError, verify(mock).foo, any(float), any(float))
    self.assertRaises(VerificationError, verify(mock).foo, any(float))
    self.assertRaises(VerificationError, verify(mock).foo, 1.1, any(float))

from test_base import *
from mockito import *

class MockitoVerificationErrorsTest(TestBase):
    
  def testPrintsNicely(self):
    mock = Mock()
    try:
      verify(mock).foo()
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo()", str(e))
      
  def testPrintsNicelyArguments(self):
    mock = Mock()
    try:
      verify(mock).foo(1, 2)
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo(1, 2)", str(e))
    
  def testPrintsNicelyStringArguments(self):
    mock = Mock()
    try:
      verify(mock).foo(1, 'foo')
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo(1, 'foo')", str(e))
      
  def testPrintsOutThatTheActualAndExpectedInvocationCountDiffers(self):
      mock = Mock()
      when(mock).foo().thenReturn(0)
      
      mock.foo()
      mock.foo()
      
      try:
          verify(mock).foo()
      except VerificationError, e:
          self.assertEquals("\nWanted times: 1, actual times: 2", str(e))
          

  #TODO implement
  def stestPrintsNicelyWhenArgumentsDifferent(self):
    mock = Mock()
    mock.foo('foo', 1)
    try:
      verify(mock).foo(1, 'foo')
    except VerificationError, e:
      self.assertEquals(
"""Arguments are different.
Wanted: foo(1, 'foo')
Actual: foo('foo', 1)""", str(e))
    
  def testPrintsUnwantedInteraction(self):
    mock = Mock()
    mock.foo(1, 'foo')
    try:
      verifyNoMoreInteractions(mock)
    except VerificationError, e:
      self.assertEquals("\nUnwanted interaction: foo(1, 'foo')", str(e))

if __name__ == '__main__':
  unittest.main()
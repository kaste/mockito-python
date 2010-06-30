from test_base import *
from mockito import mock, when, verify, VerificationError, verifyNoMoreInteractions

class VerificationErrorsTest(TestBase):
    
  def testPrintsNicely(self):
    theMock = mock()
    try:
      verify(theMock).foo()
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo()", str(e))
      
  def testPrintsNicelyOneArgument(self):
    theMock = mock()
    try:
      verify(theMock).foo("bar")
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo('bar')", str(e))

  def testPrintsNicelyArguments(self):
    theMock = mock()
    try:
      verify(theMock).foo(1, 2)
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo(1, 2)", str(e))
    
  def testPrintsNicelyStringArguments(self):
    theMock = mock()
    try:
      verify(theMock).foo(1, 'foo')
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo(1, 'foo')", str(e))
      
  def testPrintsOutThatTheActualAndExpectedInvocationCountDiffers(self):
      theMock = mock()
      when(theMock).foo().thenReturn(0)
      
      theMock.foo()
      theMock.foo()
      
      try:
          verify(theMock).foo()
      except VerificationError, e:
          self.assertEquals("\nWanted times: 1, actual times: 2", str(e))
          

  #TODO implement
  def stestPrintsNicelyWhenArgumentsDifferent(self):
    theMock = mock()
    theMock.foo('foo', 1)
    try:
      verify(theMock).foo(1, 'foo')
    except VerificationError, e:
      self.assertEquals(
"""Arguments are different.
Wanted: foo(1, 'foo')
Actual: foo('foo', 1)""", str(e))
    
  def testPrintsUnwantedInteraction(self):
    theMock = mock()
    theMock.foo(1, 'foo')
    try:
      verifyNoMoreInteractions(theMock)
    except VerificationError, e:
      self.assertEquals("\nUnwanted interaction: foo(1, 'foo')", str(e))

if __name__ == '__main__':
  unittest.main()

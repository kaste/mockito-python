from test_base import *
from mockito import *

class MockitoVerificationErrorsTest(TestBase):
    
  def testPrintsNicely(self):
    mock = Mock()
    try:
      verify(mock).foo()
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo()", e.message)
      
  def testPrintsNicelyArguments(self):
    mock = Mock()
    try:
      verify(mock).foo(1, 2)
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo(1, 2)", e.message)
    
  def testPrintsNicelyStringArguments(self):
    mock = Mock()
    try:
      verify(mock).foo(1, 'foo')
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo(1, 'foo')", e.message)
    
  def testPrintsUnwantedInteraction(self):
    mock = Mock()
    mock.foo(1, 'foo')
    try:
      verifyNoMoreInteractions(mock)
    except VerificationError, e:
      self.assertEquals("\nUnwanted interaction: foo(1, 'foo')", e.message)

if __name__ == '__main__':
  unittest.main()
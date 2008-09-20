from test_base import *
from mockito import *

class MockitoVerificationErrorsTest(TestBase):
    
  def testVerificationErrorPrintsNicely(self):
    mock = Mock()
    try:
      verify(mock).foo()
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo()", e.message)
      
  def testVerificationErrorPrintsNicelyArguments(self):
    mock = Mock()
    try:
      verify(mock).foo(1, 2)
    except VerificationError, e:
      pass
      #TODO      
#      self.assertEquals("\nWanted but not invoked: foo(1, 2)", e.message)      

if __name__ == '__main__':
  unittest.main()
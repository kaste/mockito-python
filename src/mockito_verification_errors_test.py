from test_base import *
from mockito import *

class MockitoVerificationErrorsTest(TestBase):
    
  def testVerificationErrorPrintsNicely(self):
    mock = Mock()
    try:
      verify(mock).foo()
    except VerificationError, e:
      self.assertEquals("\nWanted but not invoked: foo()", e.message)

if __name__ == '__main__':
  unittest.main()
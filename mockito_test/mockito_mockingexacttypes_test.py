from test_base import *
from mockito.invocation import InvocationError
from mockito import * 

class Foo(object):

  def bar(self):
    pass

class MockitoMockingExactTypesTest(TestBase):
  
  def testShouldScreamWhenUnknownMethodStubbed(self):
    mock = Mock(Foo)
    
    when(mock).bar().thenReturn("grr");
    
    try:
      when(mock).unknownMethod().thenReturn("grr");
      self.fail()
    except InvocationError:
      pass  
    
if __name__ == '__main__':
  unittest.main()
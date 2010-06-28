from test_base import *
from mockito.invocation import InvocationError
from mockito import mock, when 

class Foo(object):

  def bar(self):
    pass

class MockingExactTypesTest(TestBase):
  
  def testShouldScreamWhenUnknownMethodStubbed(self):
    ourMock = mock(Foo)
    
    when(ourMock).bar().thenReturn("grr");
    
    try:
      when(ourMock).unknownMethod().thenReturn("grr");
      self.fail()
    except InvocationError:
      pass  
    
  def testShouldReturnNoneWhenCallingExistingButUnstubbedMethod(self):
    ourMock = mock(Foo)
    self.assertEquals(None, ourMock.bar())
    
if __name__ == '__main__':
  unittest.main()

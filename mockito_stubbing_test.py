from test_base import *
from mockito import * 

class MockitoStubbingTest(TestBase):
  
  def testStubsWithReturnValue(self):
    mock = Mock()
    when(mock).getStuff().thenReturn("foo")
    when(mock).getMoreStuff(1, 2).thenReturn(10)
    
    self.assertEquals("foo", mock.getStuff())
    self.assertEquals(10, mock.getMoreStuff(1, 2))
    self.assertEquals(None, mock.getMoreStuff(1, 3))
    
  def testStubsWithException(self):
    mock = Mock()
    when(mock).someMethod().thenRaise(Exception("foo"))
    
    self.assertRaisesMessage("foo", mock.someMethod)

  def testStubsAndVerifies(self):
    mock = Mock()
    when(mock).foo().thenReturn("foo")
    
    self.assertEquals("foo", mock.foo())
    verify(mock).foo()

  def testStubsVerifiesAndStubsAgain(self):
    mock = Mock()
    
    when(mock).foo().thenReturn("foo")
    self.assertEquals("foo", mock.foo())
    verify(mock).foo()
    
    when(mock).foo().thenReturn("next foo")    
    self.assertEquals("next foo", mock.foo())
    verify(mock, times(2)).foo()
    
  def testOverridesStubbing(self):
    mock = Mock()
    
    when(mock).foo().thenReturn("foo")
    when(mock).foo().thenReturn("bar")
    
    self.assertEquals("bar", mock.foo())

#TODO verify after stubbing and vice versa
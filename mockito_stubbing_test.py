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

  def testStubsAndInvokesTwiceAndVerifies(self):
    mock = Mock()
    
    when(mock).foo().thenReturn("foo")
    
    self.assertEquals("foo", mock.foo())
    self.assertEquals("foo", mock.foo())

    verify(mock, times(2)).foo()

  def testStubsAndReturnValuesForMethodWithSameNameAndDifferentArguments(self):
    mock = Mock()
    when(mock).getStuff(1).thenReturn("foo")
    when(mock).getStuff(1, 2).thenReturn("bar")
    
    self.assertEquals("foo", mock.getStuff(1))
    self.assertEquals("bar", mock.getStuff(1, 2))
    
  def testStubsWithChainedReturnValues(self):
    mock = Mock()
    when(mock).getStuff().thenReturn("foo").thenReturn("bar").thenReturn("foobar")
    
    self.assertEquals("foo", mock.getStuff())
    self.assertEquals("bar", mock.getStuff())
    self.assertEquals("foobar", mock.getStuff())

  def testStubsWithChainedReturnValuesAndException(self):
    mock = Mock()
    when(mock).getStuff().thenReturn("foo").thenReturn("bar").thenRaise(Exception("foobar"))
    
    self.assertEquals("foo", mock.getStuff())
    self.assertEquals("bar", mock.getStuff())
    self.assertRaisesMessage("foobar", mock.getStuff)

  def testStubsWithChainedExceptionAndReturnValue(self):
    mock = Mock()
    when(mock).getStuff().thenRaise(Exception("foo")).thenReturn("bar")
    
    self.assertRaisesMessage("foo", mock.getStuff)
    self.assertEquals("bar", mock.getStuff())

  def testStubsWithChainedExceptions(self):
    mock = Mock()
    when(mock).getStuff().thenRaise(Exception("foo")).thenRaise(Exception("bar"))
    
    self.assertRaisesMessage("foo", mock.getStuff)
    self.assertRaisesMessage("bar", mock.getStuff)

  def testStubsWithReturnValueBeingException(self):
    mock = Mock()
    exception = Exception("foo")
    when(mock).getStuff().thenReturn(exception)
    
    self.assertEquals(exception, mock.getStuff())

#TODO verify after stubbing and vice versa
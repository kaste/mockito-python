from test_base import *
from mockito import * 

class StubbingTest(TestBase):
  
  def testStubsWithReturnValue(self):
    mock = Mock()
    when(mock).getStuff().thenReturn("foo")
    when(mock).getMoreStuff(1, 2).thenReturn(10)
    
    self.assertEquals("foo", mock.getStuff())
    self.assertEquals(10, mock.getMoreStuff(1, 2))
    self.assertEquals(None, mock.getMoreStuff(1, 3))
    
  def testStubsWhenNoArgsGiven(self):
      mock = Mock()
      when(mock).getStuff().thenReturn("foo")
      when(mock).getWidget().thenReturn("bar")
  
      self.assertEquals("foo", mock.getStuff())
      self.assertEquals("bar", mock.getWidget())     
    
  def testStubsConsecutivelyWhenNoArgsGiven(self):
      mock = Mock()
      when(mock).getStuff().thenReturn("foo").thenReturn("bar")
      when(mock).getWidget().thenReturn("baz").thenReturn("baz2")
  
      self.assertEquals("foo", mock.getStuff())
      self.assertEquals("bar", mock.getStuff())
      self.assertEquals("bar", mock.getStuff())        
      self.assertEquals("baz", mock.getWidget())
      self.assertEquals("baz2", mock.getWidget())
      self.assertEquals("baz2", mock.getWidget())
    
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
    
  def testLastStubbingWins(self):
    mock = Mock()
    when(mock).foo().thenReturn(1)
    when(mock).foo().thenReturn(2)
    
    self.assertEquals(2, mock.foo())
    
  def testStubbingOverrides(self):
    mock = Mock()
    when(mock).foo().thenReturn(1)
    when(mock).foo().thenReturn(2).thenReturn(3)
    
    self.assertEquals(2, mock.foo())    
    self.assertEquals(3, mock.foo())    
    self.assertEquals(3, mock.foo())   
    
  def testStubsWithMatchers(self):
    mock = Mock()
    when(mock).foo(any()).thenReturn(1)
    
    self.assertEquals(1, mock.foo(1))    
    self.assertEquals(1, mock.foo(100))   
    
  def testStubbingOverrides2(self):
    mock = Mock()
    when(mock).foo(any()).thenReturn(1)
    when(mock).foo("oh").thenReturn(2)
    
    self.assertEquals(2, mock.foo("oh"))    
    self.assertEquals(1, mock.foo("xxx"))   
    
  def testDoesNotVerifyStubbedCalls(self):
    mock = Mock()
    when(mock).foo().thenReturn(1)

    verify(mock, times=0).foo()

  def testStubsWithMultipleReturnValues(self):
    mock = Mock()
    when(mock).getStuff().thenReturn("foo", "bar", "foobar")
    
    self.assertEquals("foo", mock.getStuff())
    self.assertEquals("bar", mock.getStuff())
    self.assertEquals("foobar", mock.getStuff())

  def testStubsWithChainedMultipleReturnValues(self):
    mock = Mock()
    when(mock).getStuff().thenReturn("foo", "bar").thenReturn("foobar")
    
    self.assertEquals("foo", mock.getStuff())
    self.assertEquals("bar", mock.getStuff())
    self.assertEquals("foobar", mock.getStuff())

  def testStubsWithMultipleExceptions(self):
    mock = Mock()
    when(mock).getStuff().thenRaise(Exception("foo"), Exception("bar"))
    
    self.assertRaisesMessage("foo", mock.getStuff)
    self.assertRaisesMessage("bar", mock.getStuff)

  def testStubsWithMultipleChainedExceptions(self):
    mock = Mock()
    when(mock).getStuff().thenRaise(Exception("foo"), Exception("bar")).thenRaise(Exception("foobar"))
    
    self.assertRaisesMessage("foo", mock.getStuff)
    self.assertRaisesMessage("bar", mock.getStuff)
    self.assertRaisesMessage("foobar", mock.getStuff)

#TODO verify after stubbing and vice versa

if __name__ == '__main__':
  unittest.main()

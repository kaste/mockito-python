from test_base import *
from mockito import *

# TODO: add more test cases (create a base test class for both static and class methods?)

class Dog():
  @classmethod
  def bark(cls):
    return "woof!"
  
class Cat():
  @classmethod
  def meow(cls, m):
    return str(cls) + " " + str(m)

class MockitoClassMethodsTest(TestBase):   

  def tearDown(self):
    unstub() 

  def testUnstubs(self):     
    when(Dog).bark().thenReturn("miau!")
    unstub()
    self.assertEquals("woof!", Dog.bark())
  
  def testStubs(self):     
    self.assertEquals("woof!", Dog.bark())
    
    when(Dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
  def testVerifiesMultipleCallsOnClassmethod(self):     
    when(Dog).bark().thenReturn("miau!")

    Dog.bark()
    Dog.bark()
    
    verify(Dog, times(2)).bark()
    
  def testFailsVerificationOfMultipleCallsOnClassmethod(self):
    when(Dog).bark().thenReturn("miau!")

    Dog.bark()
    
    self.assertRaises(VerificationError, verify(Dog, times(2)).bark)

  def testStubsAndVerifiesClassmethod(self):
    when(Dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
    verify(Dog).bark()
    
  def testPreservesClassArgumentAfterUnstub(self):
    self.assertEquals("__main__.Cat foo", Cat.meow("foo"))

    when(Cat).meow("foo").thenReturn("bar")
    
    self.assertEquals("bar", Cat.meow("foo"))
    
    unstub()
    
    self.assertEquals("__main__.Cat foo", Cat.meow("foo"))
    
if __name__ == '__main__':
  unittest.main()    
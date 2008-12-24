from test_base import *
from mockito import *

class Dog:
  @classmethod
  def bark(cls):
    return "woof!"
  
class Cat:
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
  
  #TODO decent test case please :) without testing irrelevant implementation details
  def testUnstubShouldPreserveMethodType(self):
    when(Dog).bark().thenReturn("miau!")
    unstub()
    self.assertTrue(isinstance(Dog.__dict__.get("bark"), classmethod))     
  
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
    self.assertTrue(Cat.meow("foo").endswith("Cat foo"))

    when(Cat).meow("foo").thenReturn("bar")
    
    self.assertEquals("bar", Cat.meow("foo"))
    
    unstub()
    
    self.assertTrue(Cat.meow("foo").endswith("Cat foo"))
    
if __name__ == '__main__':
  unittest.main()
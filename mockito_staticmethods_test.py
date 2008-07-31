from test_base import *
from mockito import *

class Dog():
  @staticmethod
  def bark():
    return "woof!"

class Cat():
  @staticmethod
  def meow():
    return "miau!"

class MockitoStaticmethodsTest(TestBase):   

  def testVerifiesMultipleCallsOnClassmethod(self):     
    dog = ClassMock(Dog)
    when(dog).bark().thenReturn("miau!")

    for i in range(0, 10): Dog.bark()
    
    verify(dog, times(10)).bark()
    
  def testFailsVerificationOfMultipleCallsOnClassmethod(self):
    dog = ClassMock(Dog)
    when(dog).bark().thenReturn("miau!")

    Dog.bark()
    
    self.assertRaises(VerificationError, verify(dog, times(2)).bark)

  def testStubsAndVerifiesClassmethod(self):
    dog = ClassMock(Dog)
    when(dog).bark().thenReturn("miau!")
    
    self.assertEquals("miau!", Dog.bark())
    
    verify(dog).bark()

  # TODO: fix the code for failing test
  #def testStubsTwoMethodsFromTwoDifferentClasses(self):
  #  dog = ClassMock(Dog)
  #  when(dog).bark().thenReturn("miau!")
  #  cat = ClassMock(Cat)
  #  when(cat).meow().thenReturn("woof!")
  #  
  #  self.assertEquals("miau!", Dog.bark())
  #  self.assertEquals("woof!", Cat.meow())
